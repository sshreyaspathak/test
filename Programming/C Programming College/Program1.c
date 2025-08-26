// write a program to count frequency of each element of an array with given array ( 1 , 3,9,4,1,2,5,2,5,3)

#include <stdio.h>

int main() {
    int arr[] = {1, 3, 9, 4, 1, 2, 5, 2, 5, 3};
    int freq[10] = {0};
    int n = sizeof(arr) / sizeof(arr[0]);

    for (int i = 0; i < n; i++) {
        freq[arr[i]]++;
    }

    printf("Element\tFrequency\n");
    for (int i = 0; i < 10; i++) {
        if (freq[i] != 0) {
            printf("%d\t%d\n", i, freq[i]);
        }
    }

    return 0;
}
