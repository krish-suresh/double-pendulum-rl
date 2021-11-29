fn main() {
    // let mut div = vec!(1..20);
    // for i in div.iter().rev() {
    //     for j in div {
    //         if *i == j {
    //             break;
    //         }
    //         if i % j == 0 {
    //             div.pop(j);
    //         }
    //     }
    // }
    // println!("{}", div);
    let div = [11,12,13,14,16,17,18,19,20];
    let mut x = 2520;
    let answer = loop {
        let mut a = true;
        for i in div {
            if x % i != 0 {
                a = false;
                break;
            }
        }
        if a {
            break x;
        }
        x+=1;
    };
    println!("{}", answer);
}