#include <string.h>
#include <unistd.h>

#include "GUI/gui.h"
#include "GUI/gui_optionbrowser.h"
#include "prompts/PromptWindows.h"
#include "language/gettext.h"
#include "themes/CTheme.h"
#include "FileOperations/fileops.h"
#include "menu.h"
#include "sys.h"
#include "riivolutionmenu.h"

int RiivolutionMenu(const char *gameID)
{
    int choice = 0;
    bool exit = false;

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
    snprintf(riivolutionFolderPath, sizeof(riivolutionFolderPath), "%s%s", Settings.Riivolutionpath, gameID);

    if (!CheckFile(riivolutionFolderPath)) {
        choice = WindowPrompt(tr("Error"), tr("Riivolution folder not found. Create it?"), tr("Yes"), tr("Cancel"));
        if (choice == 0) {
            return choice;
        } else {
            if (!CreateSubfolder(riivolutionFolderPath)) {
                return -1;
            }
        }
    }

    u64 directorySize = GetDirectorySize(riivolutionFolderPath);
    if (directorySize == 0) {
        choice = WindowPrompt(tr("Error"), tr("Your game's Riivolution folder is empty. Delete it?"), tr("Yes"), tr("Cancel"));
        if (choice == 0) {
            return choice;
        } else {
            if (!RemoveDirectory(riivolutionFolderPath)) {
                return -1;
            }
        }
    } else {
        // Riivolution
    }

    return choice;
}
