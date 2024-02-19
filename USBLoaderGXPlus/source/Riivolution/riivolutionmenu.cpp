#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>

#include "GUI/gui.h"
#include "GUI/gui_optionbrowser.h"
#include "prompts/PromptWindows.h"
#include "language/gettext.h"
#include "themes/CTheme.h"
#include "FileOperations/fileops.h"
#include "menu.h"
#include "sys.h"
#include "gct.h"

/****************************************************************************
 * RiivolutionMenu
 ***************************************************************************/
int RiivolutionMenu(const char *gameID)
{
    int choice = 0;
    bool exit = false;
    int ret = 1;

    GuiImageData btnOutline(Resources::GetFile("button_dialogue_box.png"), Resources::GetFileSize("button_dialogue_box.png"));
    GuiImageData settingsbg(Resources::GetFile("settings_background.png"), Resources::GetFileSize("settings_background.png"));
    GuiImage settingsbackground(&settingsbg);

    GuiTrigger trigA;
    trigA.SetSimpleTrigger(-1, WPAD_BUTTON_A | WPAD_CLASSIC_BUTTON_A, PAD_BUTTON_A);
    GuiTrigger trigB;
    trigB.SetButtonOnlyTrigger(-1, WPAD_BUTTON_B | WPAD_CLASSIC_BUTTON_B, PAD_BUTTON_B);

    GuiText backBtnTxt(tr("Back"), 22, thColor("r=0 g=0 b=0 a=255 - prompt windows button text color"));
    backBtnTxt.SetMaxWidth(btnOutline.GetWidth() - 30);
    GuiImage backBtnImg(&btnOutline);
    GuiButton backBtn(&backBtnImg, &backBtnImg, 2, 3, -195, 400, &trigA, NULL, btnSoundClick2, 1);
    backBtn.SetLabel(&backBtnTxt);
    backBtn.SetTrigger(&trigB);

    char riivolutionFolderPath[120];
    snprintf(riivolutionFolderPath, sizeof(riivolutionFolderPath), "%s%s/", Settings.Riivolutionpath, gameID);

    DIR *dir = opendir(riivolutionFolderPath);
    if (!dir) {
        choice = WindowPrompt(tr("Error"), tr("Riivolution folder not found. Create it?"), tr("Yes"), tr("Cancel"));
        if (choice) {
            CreateSubfolder(riivolutionFolderPath);
        } else {
            return choice;
        }
    } else {
        closedir(dir);

        struct dirent *entry;
        dir = opendir(riivolutionFolderPath);
        bool folderIsEmpty = true;

        while ((entry = readdir(dir)) != NULL) {
            if (entry->d_type == DT_REG && strstr(entry->d_name, ".xml") != NULL) {
                folderIsEmpty = false;
                break;
            }
        }

        closedir(dir);

        if (folderIsEmpty) {
            choice = WindowPrompt(tr("Error"), tr("Riivolution folder is empty. Delete it?"), tr("Yes"), tr("Cancel"));
            if (choice) {
                RemoveFolder(riivolutionFolderPath);
            } else {
                return choice;
            }
        }
    }

    // Riivolution here..

    return choice;
}
