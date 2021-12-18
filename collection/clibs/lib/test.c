#include <stdio.h>
#include <stdlib.h>

#define MAX_SLOTS 3000

int          arr[MAX_SLOTS];
unsigned int cursor_position = (MAX_SLOTS - 1);

int main(int narg, char *argv[], char *penv[]) {
    while (cursor_position) {
        arr[cursor_position] = cursor_position;
        cursor_position--;
    }
    while ((cursor_position) < MAX_SLOTS) {
        printf("arr [%d]: %d\n", cursor_position, arr[cursor_position]);
        cursor_position++;
    }
    return 0;
}
