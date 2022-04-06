// package test

// // func test1(n int) {
// // 	n = n + x
// // 	func l() {
// // 		n = n+1
// // 	}
// // }

// var x int
// func factorial(n int) int {
// 	var f int
// 	if n == 0 {
// 		f = 1
// 	}

//   	if n!= 0 {
// 		f = n * (n-1)//factorial(n-1)
// 	}
// 	return f
// }

// var n int
// func main() {
//   	n = 0
// 	// factorial(n)
// 	for n < 10 {
// 		n = n + 1
//     	// # x = n
// 		var x int
// 		x = factorial(n)
// 	}
// 	return x
// }

package main

func rescuive(i int) int {

	if i == 1 {
		return 1
	}
	if i == 0 {
		return 0
	}
	return rescuive(i-1) + rescuive(i-2)
}

func main() {
	var i int
	i = 10
	var sum int
	// for i<10 {
	sum = rescuive(i)
	// 	i = i+1
	// }
	return sum

}
