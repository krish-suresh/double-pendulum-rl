clear
clc
clf
global dt l_1 l_2 m_0 m_1 m_2 g u;
dt = 0.01;
l_1 = 0.1; 
l_2 = 0.1; 
m_0 = 1; 
m_1 = 0.5; 
m_2 = 0.5;

g = 9.81;
u = 0;
simulatePendulumWithSlider();
% hits either wall, reward function gets below a threshhold
% reward function = angWrap(0-theta_1) + angWrap(0-theta_1);

function simulatePendulumWithSlider()
    global dt u;
    y = [0.5 pi pi];
    y_dot = zeros(1, 3);
    x = [y; y_dot];
    w = zeros(1,3);
    
    plotPendulum(x);
    fig = uifigure;
    u_slider = uislider(fig,'Position',[100 75 300 3],...
               'ValueChangingFcn',@(sld,event) updateU(event.Value));
    u_slider.Limits = [-5 5];
    u_slider.Value = 0;
    while true
        x = simPendulumStep(x, u, w);
        plotPendulum(x);
        pause(dt);
    end
end

function updateU(new_u)
    global u;
    u = new_u;
end
function x = simPendulumStep(x, u, w)
    global dt l_1 l_2 m_0 m_1 m_2 g;

    y = x(1, :);
    y_dot = x(2, :);
    y_new = zeros(1,3);
    y_dot_new = zeros(1,3);
    d = zeros(1,3);
%     d = [y_dot(1)*0.001 y_dot(1)*0.0001 y_dot(1)*0.0001];

    if y(1)<0.005
        y_dot(1) = 0;
        u = max(u,0);
    elseif y(1)>0.995
        y_dot(1) = 0;
        u = min(u,0);
    end
%     disp(u);
    M = [m_0+m_1+m_2, l_1*(m_1+m_2)*cos(y(2)), m_2*l_2*cos(y(3));... 
        l_1*(m_1+m_2)*cos(y(2)), l_1^2*(m_1+m_2), l_1*l_2*m_2*cos(y(2)-y(3));... 
        l_2*m_2*cos(y(3)), l_1*l_2*m_2*cos(y(2)-y(3)), l_2^2*m_2];
    
    
    f = [l_1*(m_1+m_2)*(y_dot(2)^2)*sin(y(2))+m_2*l_2*(y_dot(3)^2)*sin(y(3));... 
        -l_1*l_2*m_2*(y_dot(3)^2)*sin(y(2)-y(3))+g*(m_1+m_2)*l_1*sin(y(2)); ...
        l_1*l_2*m_2*(y_dot(2)*2)*sin(y(2)-y(3))+g*l_2*m_2*sin(y(3))]... 
    - d' + [u 0 0]' + w';

    y_dot_dot = (M\f)';

    for i=1:3        
        y_dot_new(i) = y_dot(i) + y_dot_dot(i)*dt;
        y_new(i) = y(i) + y_dot_new(i)*dt + (y_dot_dot(i)*dt^2)/2;
    end
    if y_new(1)<0
        y_new(1) = 0;
    elseif y_new(1)>1
        y_new(1) = 1;
    end
    x = [y_new; y_dot_new];
end

function plotPendulum(x)
    global l_1 l_2;

    TRACK_LENGTH = 1;
    CART_WIDTH = 0.05;
    CART_HEIGHT = 0.05;
    y = x(1,:);
    
    clf
    hold on
    % Plot Track
    plot([0 TRACK_LENGTH], [0 0])
    % Plot Cart
    rectangle('Position',[y(1)-CART_WIDTH/2 0-CART_HEIGHT/2 CART_WIDTH CART_HEIGHT])
    % Plot Bar 1
    bar_1_x = y(1)+sin(y(2))*l_1*2;
    bar_1_y = cos(y(2))*l_1*2;
    plot([y(1) bar_1_x], [0 bar_1_y])
    % Plot Bar 2
    plot([bar_1_x bar_1_x+sin(y(3))*l_2*2], [bar_1_y bar_1_y+cos(y(3))*l_2*2])

    axis([0 1 -0.5 0.5])
    hold off
end
