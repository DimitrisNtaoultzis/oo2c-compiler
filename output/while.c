#include <stdio.h>
#include <stdlib.h>

typedef struct Main Main;

struct Main {
   int x;
};

void Main_main__0(Main* self) {
   int i;
   scanf("%d", &i);
   while ((i < 5)) {
      if ((i == 3)) {
         printf("%d\n", i);
      }
      else {
         printf("%d\n", 8);
      }
      i = (i + 1);
   }
}


int main(void) {
   Main* self = (Main*)malloc(sizeof(Main));
   Main_main__0(self);
   return 0;
}
