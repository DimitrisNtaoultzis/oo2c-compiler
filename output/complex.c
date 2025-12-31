#include <stdio.h>
#include <stdlib.h>

typedef struct Complex Complex;
typedef struct Main Main;

struct Complex {
   int real;
   int img;
};

struct Main {
   Complex* c1;
   Complex* c2;
   Complex* c3;
};

Complex* Complex___init____0(Complex* self) {
   self->real = 0;
   self->img = 0;
   return self;
   return self;
}

Complex* Complex___init____2(Complex* self, int real, int img) {
   self->real = real;
   self->img = img;
   return self;
   return self;
}

Complex* Complex_get_complex__0(Complex* self) {
   return self;
   return self;
}

void Complex_set_complex__2(Complex* self, int real, int img) {
   self->real = real;
   self->img = img;
}

void Complex_set_real__1(Complex* self, int r) {
   self->real = r;
}

void Complex_set_img__1(Complex* self, int i) {
   self->img = i;
}

int Complex_get_real__0(Complex* self) {
   return self->real;
}

int Complex_get_img__0(Complex* self) {
   return self->img;
}

int Complex_squared_modulus__0(Complex* self) {
   return ((self->real * self->real) + (self->img * self->img));
}

void Complex_add__2(Complex* self, Complex* c1, Complex* c2) {
   self->real = (c1->real + c2->real);
   self->img = (c1->img + c2->img);
}

void Complex_print_complex__0(Complex* self) {
   printf("%d %d\n", self->real, self->img);
}

void Main_main__0(Main* self) {
   self->c1 = (Complex*)malloc(sizeof(Complex));
   Complex___init____2(self->c1, 1, 2);
   self->c2 = (Complex*)malloc(sizeof(Complex));
   Complex___init____2(self->c2, 3, 4);
   self->c3 = (Complex*)malloc(sizeof(Complex));
   Complex___init____0(self->c3);
   Complex_print_complex__0(self->c1);
   Complex_print_complex__0(self->c2);
   Complex_add__2(self->c3, self->c1, self->c2);
   Complex_print_complex__0(self->c3);
   Complex_set_real__1(self->c3, Complex_squared_modulus__0(self->c1));
   Complex_set_img__1(self->c3, Complex_squared_modulus__0(self->c2));
   Complex_print_complex__0(self->c3);
}


int main(void) {
   Main* self = (Main*)malloc(sizeof(Main));
   Main_main__0(self);
   return 0;
}
