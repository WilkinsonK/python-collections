
int Cfibonacci(int n) {
    if (n < 2) { return 1; }
    return Cfibonacci(n - 1) + Cfibonacci(n - 2);
}

// START_BODY

int Cfibonacci(int n);
