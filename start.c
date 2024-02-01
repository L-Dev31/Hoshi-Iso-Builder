#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// literally a function to convert riivolution XML files to Gecko Code Lists
// done fast cuz I am fast as feck boiiiii

typedef uint8_t u1;
typedef uint32_t u4;

bool compare_strings(void * str1_ptr, void * str2_ptr, u4 last_pos_check);

int main(int argc, char * argv[])
{
  FILE * fp = fopen(argv[1], "rb");
  FILE * cdlist_fp = fopen("codelist.txt", "w");
  
  // variables
  char mem_tag[] = "memory";
  char mem_tag_read[7] = {0};
  char offset_tag[] = "offset";
  char offset_tag_read[7] = {0};
  char valuefile_tag[] = "valuefile";
  char valuefile_tag_read[10] = {0};
  char value_tag[] = "value";
  char value_tag_read[6] = {0};
  
  char custom_code_loader_name_1[256] = "CustomCode/Loader";
  char custom_code_loader_name_1_read[256] = {0};
  
  u4 offset = 0; // to store offset addresses
  // temp var
  u4 temp = 0;
  int temp1 = 0;
  int temp2 = 0;
  
  char ch = 0;
  while ((ch = fgetc(fp)) != EOF)
  {
    // tag reached
    if (ch == '<')
    {
      for (int i = 0; i < 6; i++)
        mem_tag_read[i] = fgetc(fp);
      
      // memory tag reached
      if (compare_strings(mem_tag_read, mem_tag, 0))
      {
        // get offset
        ch = fgetc(fp); // space
        for (int i = 0; i < 6; i++)
          offset_tag_read[i] = fgetc(fp);
        
        // offset found
        if (compare_strings(offset_tag_read, offset_tag, 0))
        {
          ch = fgetc(fp); // equal sign
          ch = fgetc(fp); // openning single/double quote
          fscanf(fp, "%X", &offset);
          fprintf(cdlist_fp, "%08X ", offset - 0x7C000000);
          
          ch = fgetc(fp); // closing single/double quote
          ch = fgetc(fp); // space
          
          // search for either valuefile or value tag
          temp = ftell(fp);
          for (int i = 0; i < 9; i++)
            valuefile_tag_read[i] = fgetc(fp);
          
          // read again for value tag
          fseek(fp, temp, SEEK_SET);
          for (int i = 0; i < 5; i++)
            value_tag_read[i] = fgetc(fp);
          
          // read again from tag start
          fseek(fp, temp, SEEK_SET);
          
          // valuefile reached!
          if (compare_strings(valuefile_tag_read, valuefile_tag, 0))
          {
            // skip valuefile="/'
            for (int i = 0; i < 11; i++)
              fgetc(fp);
            
            // store this position
            temp = ftell(fp);
            
            // get custom code loader first name part
            for (int i = 0; i < 17; i++)
              custom_code_loader_name_1_read[i] = fgetc(fp);
            
            // custom code loader name reached!
            if (compare_strings(custom_code_loader_name_1_read, custom_code_loader_name_1, 0))
            {
              // complete the name
              custom_code_loader_name_1_read[17] = argv[2][0];
              custom_code_loader_name_1_read[18] = '.';
              custom_code_loader_name_1_read[19] = 'r';
              custom_code_loader_name_1_read[20] = 'e';
              custom_code_loader_name_1_read[21] = 'l';
              
              // dump loader binary data on codelist.txt
              FILE * loader_fp = fopen(custom_code_loader_name_1_read, "rb");
              for (int i = 0; (temp1 = fgetc(loader_fp)) != EOF; i++)
              {
                if (i % 4 == 0 && i != 0)
                {
                  fprintf(cdlist_fp, "\n");
                  offset += 4;
                  fprintf(cdlist_fp, "%08X ", offset - 0x7C000000);
                }
                fprintf(cdlist_fp, "%02X", temp1);
              }
              // close loader file
              fclose(loader_fp);
            }
          }
          // value reached!
          else if (compare_strings(value_tag_read, value_tag, 0))
          {
            // skip value="/'
            for (int i = 0; i < 7; i++)
              fgetc(fp);
              
            // store this position
            temp = ftell(fp);
            
            // dump value into codelist
            for (int i = 0; (temp1 = fgetc(fp)) != '\'' && temp1 != '\"'; i++)
              {                
                if (i % 8 == 0 && i != 0)
                {
                  fprintf(cdlist_fp, "\n");
                  offset += 4;
                  fprintf(cdlist_fp, "%08X ", offset - 0x7C000000);
                }
                fprintf(cdlist_fp, "%c", temp1);
              }
          }
          else
          {
            printf("Excuse me what?\n");
            return 0;
          }
          
          // print newline
          fprintf(cdlist_fp, "\n");
        }
        else
          continue;
      }
      else
        continue;
    }
    else
      continue;
  }
}


// compare_strings() function
// function to compare 2 strings (null terminated)
// used to compare file start strings to check for the
// binary file being read
//
// str1_ptr (void *) --> pointer to the string 1
// str2_ptr (void *) --> pointer to the string 2
// last_pos_check (u4) --> check if both strings are valid up to a position. If 0
//                         is passed treat both as normal strings (null terminated)
bool compare_strings(void * str1_ptr, void * str2_ptr, u4 last_pos_check)
{
  // cast both pointers to be u1 * type
  u1 * str1 = (u1 *) str1_ptr; 
  u1 * str2 = (u1 *) str2_ptr;
  int i = 0;
  while (1)
  {
    // character array treatment
    if (last_pos_check == i && last_pos_check != 0)
      break;
    // normal string treatment
    if (*(str1 + i) == '\0' && *(str2 + i) == '\0')
      break;
    // character comparison
    if (*(str1 + i) != *(str2 + i))
      return false;
    i++;
  }
  
  // if everything is good, return true
  return true;
}
