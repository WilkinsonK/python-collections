#include <stdio.h>
#include <stdlib.h>


int Cmodulo(int n, int m)
{
    return n % m;
}

int Cpower(int n, int p)
{
    int ret = 1;
    for (int i = 0; i < p; i++) {
        ret = ret * n;
    }
    return ret;
}

int CisPrime(int n)
{
    if (n <= 1) return 0;
    if (n <= 3) return 1;
    if (!Cmodulo(n, 2) || !Cmodulo(n, 3)) return 0;

    int step = 5;
    while (Cpower(step, 2) <= n) {
        if (!Cmodulo(n, step) || !Cmodulo(n, step + 2)) {
            return 0;
        }
        step += 6;
    }
    return 1;
}

int CgetNextPrime(int n)
{
    if (n == 1 || n == 2) return n + 1;

    n += 2;
    while (!CisPrime(n)) { n += 2; }
    return n;
}

int Cfibonacci(int n) {
    if (n < 2) { return 1; }
    return Cfibonacci(n - 1) + Cfibonacci(n - 2);
}

// START_BODY

int Cpower(int n, int p);
int Cmodulo(int n, int m);
int CisPrime(int n);
int CgetNextPrime(int n);
int Cfibonacci(int n);
