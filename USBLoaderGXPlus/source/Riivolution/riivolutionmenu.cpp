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

/****************************************************************************
 * RiivolutionMenu 
 * L-DEV 2024
 * The source code as well as any code uses are the property of USBLoaderGX and Riivolution
 * Use this functionality at your own risk; I do not endorse any issues, and it is your responsibility to use this tool in a legal manner.
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
    snprintf(riivolutionFolderPath, sizeof(riivolutionFolderPath), "%s%s/", Settings.XmlRiivolutionpath, gameID);

    if (!DirectoryExist(riivolutionFolderPath))
    {
        choice = WindowPrompt(tr("Error"), tr("Riivolution folder not found. Create it?"), tr("Yes"), tr("Cancel"));
        if (choice)
        {
            CreateSubfolder(riivolutionFolderPath);
        }
        else
        {
            return choice;
        }
    }

    OptionList riivolutionFiles;
    GuiOptionBrowser riivolutionBrowser(400, 280, &riivolutionFiles, "bg_options_settings.png");
    riivolutionBrowser.SetPosition(0, 90);
    riivolutionBrowser.SetAlignment(ALIGN_CENTER, ALIGN_TOP);
    riivolutionBrowser.SetClickable(true);

    GuiText titleTxt(gameID, 28, (GXColor){0, 0, 0, 255});
    titleTxt.SetAlignment(ALIGN_CENTER, ALIGN_TOP);
    titleTxt.SetMaxWidth(350, SCROLL_HORIZONTAL);
    titleTxt.SetPosition(12, 40);

    ListDirectory(riivolutionFolderPath, &riivolutionFiles);

    HaltGui();
    GuiWindow w(screenwidth, screenheight);
    w.Append(&settingsbackground);
    w.Append(&titleTxt);
    w.Append(&backBtn);
    w.Append(&riivolutionBrowser);
    mainWindow->SetState(STATE_DISABLED);
    mainWindow->Append(&w);
    ResumeGui();

    while (!exit)
    {
        usleep(100000);

        ret = riivolutionBrowser.GetClickedOption();
        if (ret >= 0)
        {
            const char *riivolutionFile = riivolutionFiles.GetValue(ret);
            // Riivolution logic
        }

        if (backBtn.GetState() == STATE_CLICKED)
        {
            backBtn.ResetState();
            exit = true;
            break;
        }
    }

    HaltGui();
    mainWindow->SetState(STATE_DEFAULT);
    mainWindow->Remove(&w);
    ResumeGui();

    return choice;
}
