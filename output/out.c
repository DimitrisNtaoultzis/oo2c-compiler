#include <stdio.h>
#include <stdlib.h>

typedef struct Shape Shape;
typedef struct Circle Circle;
typedef struct Square Square;
typedef struct SquareWithCirclesOnCorners SquareWithCirclesOnCorners;
typedef struct SquareWithCirclesOnCorners2 SquareWithCirclesOnCorners2;
typedef struct Main Main;

struct Shape {
   int x;
   int y;
   int color;
};

struct Circle {
   int x;
   int y;
   int color;
   int radius;
};

struct Square {
   int x;
   int y;
   int color;
   int side;
};

struct SquareWithCirclesOnCorners {
   int x;
   int y;
   int color;
   int side;
   int radius;
};

struct SquareWithCirclesOnCorners2 {
   Square* s;
   Circle* c;
};

struct Main {
   Circle* c;
   Square* s;
   SquareWithCirclesOnCorners* s1;
   SquareWithCirclesOnCorners2* s2;
};

Shape* Shape___init____2(Shape* self, int x, int y) {
   self->x = x;
   self->y = y;
   return self;
}

Shape* Shape___init____3(Shape* self, int x, int y, int color) {
   self->x = x;
   self->y = y;
   self->color = color;
   return self;
}

void Shape_move__2(Shape* self, int dx, int dy) {
   self->x = (self->x + dx);
   self->y = (self->y + dy);
}

void Shape_move__1(Shape* self, int dx) {
   self->x = (self->x + dx);
}

void Shape_set_x__1(Shape* self, int x) {
   self->x = x;
}

int Shape_get_x__0(Shape* self) {
   return self->x;
}

Circle* Circle___init____1(Circle* self, int radius) {
   self->radius = radius;
   return self;
}

Circle* Circle___init____4(Circle* self, int x, int y, int color, int radius) {
   self->x = x;
   self->y = y;
   self->color = color;
   self->radius = radius;
   return self;
}

int Circle_get_radius__0(Circle* self) {
   return self->radius;
}

int Circle_area__0(Circle* self) {
   int int_pi;
   int_pi = 3;
   return ((int_pi * self->radius) * self->radius);
}

Square* Square___init____1(Square* self, int side) {
   self->side = side;
   return self;
}

int Square_get_side__0(Square* self) {
   return self->side;
}

int Square_area__0(Square* self) {
   return (self->side * self->side);
}

SquareWithCirclesOnCorners* SquareWithCirclesOnCorners___init____2(SquareWithCirclesOnCorners* self, int side, int radius) {
   self->side = side;
   self->radius = radius;
   return self;
}

int SquareWithCirclesOnCorners_area__0(SquareWithCirclesOnCorners* self) {
   int int_pi;
   int_pi = 3;
   return ((Square_get_side__0((Square*)self) * Square_get_side__0((Square*)self)) + (((3 * int_pi) * Circle_get_radius__0((Circle*)self)) * Circle_get_radius__0((Circle*)self)));
}

SquareWithCirclesOnCorners2* SquareWithCirclesOnCorners2___init____2(SquareWithCirclesOnCorners2* self, int side, int radius) {
   self->s = (Square*)malloc(sizeof(Square));
   Square___init____1(self->s, side);
   self->c = (Circle*)malloc(sizeof(Circle));
   Circle___init____1(self->c, radius);
   return self;
}

int SquareWithCirclesOnCorners2_area__1(SquareWithCirclesOnCorners2* self, SquareWithColors* squarewithcolors) {
   int int_pi_part;
   int_pi_part = 3;
   return ((Square_get_side__0(self->s) * Square_get_side__0(self->s)) + (((3 * int_pi_part) * Circle_get_radius__0(self->c)) * Circle_get_radius__0(self->c)));
}

void Main_main__0(Main* self) {
   self->c = (Circle*)malloc(sizeof(Circle));
   Circle___init____1(self->c, 4);
   printf("%d\n", Circle_area__0(self->c));
   self->s = (Square*)malloc(sizeof(Square));
   Square___init____1(self->s, 4);
   printf("%d\n", Square_area__0(self->s));
   self->s1 = (SquareWithCirclesOnCorners*)malloc(sizeof(SquareWithCirclesOnCorners));
   SquareWithCirclesOnCorners___init____2(self->s1, 3, 5);
   self->s2 = (SquareWithCirclesOnCorners2*)malloc(sizeof(SquareWithCirclesOnCorners2));
   SquareWithCirclesOnCorners2___init____2(self->s2, 3, 5);
   printf("%d\n", SquareWithCirclesOnCorners2_area__1(self->s2, self->s1));
}


int main(void) {
   Main* self = (Main*)malloc(sizeof(Main));
   Main_main__0(self);
   return 0;
}
