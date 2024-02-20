/****************************************************************************
 * Copyright (C) 2011
 * by Dimok
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any
 * damages arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any
 * purpose, including commercial applications, and to alter it and
 * redistribute it freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you
 * must not claim that you wrote the original software. If you use
 * this software in a product, an acknowledgment in the product
 * documentation would be appreciated but is not required.
 *
 * 2. Altered source versions must be plainly marked as such, and
 * must not be misrepresented as being the original software.
 *
 * 3. This notice may not be removed or altered from any source
 * distribution.
 ***************************************************************************/
#include <string.h>
#include <unistd.h>

#include "RiivolutionMenu.h"
#include "language/gettext.h"
#include "prompts/PromptWindows.h"
#include "prompts/ProgressWindow.h"
#include "FileOperations/DirList.h"
#include "FileOperations/fileops.h"
#include "sys.h"
#include "menu/menus.h"
#include "utils/ShowError.h"
#include "utils/tools.h"
#include "gecko.h"


RiivolutionMenu::RiivolutionMenu()
	: FlyingButtonsMenu(tr("Riivolution Menu"))
{
	delete MainButtonImgData;
	delete MainButtonImgOverData;

	MainButtonImgData = Resources::GetImageData("Riivolution_box.png");
	MainButtonImgOverData = NULL;

	ParentMenu = MENU_SETTINGS;

	for(int i = 0; i < 4; ++i)
		RiivolutionPreviews[i] = NULL;

	defaultBtnTxt = new GuiText(tr( "Default" ), 22, thColor("r=0 g=0 b=0 a=255 - prompt windows button text color"));
	defaultBtnTxt->SetMaxWidth(btnOutline->GetWidth() - 30);
	defaultBtnImg = new GuiImage(btnOutline);
	if (Settings.wsprompt)
	{
		defaultBtnTxt->SetWidescreen(Settings.widescreen);
		defaultBtnImg->SetWidescreen(Settings.widescreen);
	}
	defaultBtn = new GuiButton(btnOutline->GetWidth(), btnOutline->GetHeight());
	defaultBtn->SetAlignment(ALIGN_CENTER, ALIGN_TOP);
	defaultBtn->SetPosition(-20, 400);
	defaultBtn->SetLabel(defaultBtnTxt);
	defaultBtn->SetImage(defaultBtnImg);
	defaultBtn->SetSoundOver(btnSoundOver);
	defaultBtn->SetSoundClick(btnSoundClick2);
	defaultBtn->SetTrigger(trigA);
	defaultBtn->SetEffectGrow();
	Append(defaultBtn);

	backBtn->SetPosition(-205, 400);
}

RiivolutionMenu::~RiivolutionMenu()
{
	HaltGui();
	for(u32 i = 0; i < MainButton.size(); ++i)
		Remove(MainButton[i]);
	Remove(defaultBtn);

	delete defaultBtn;
	delete defaultBtnTxt;
	delete defaultBtnImg;
	for(int i = 0; i < 4; ++i)
		delete RiivolutionPreviews[i];
}

int RiivolutionMenu::Execute()
{
	RiivolutionMenu * Menu = new RiivolutionMenu();
	mainWindow->Append(Menu);

	Menu->ShowMenu();

	int returnMenu = MENU_NONE;

	while((returnMenu = Menu->MainLoop()) == MENU_NONE);

	delete Menu;

	return returnMenu;
}

int RiivolutionMenu::MainLoop()
{
	if(defaultBtn->GetState() == STATE_CLICKED)
	{
		int choice = WindowPrompt(0, tr("Do you want to deactivate all mods?"), tr("Yes"), tr("Cancel"));
		if(choice)
		{
			HaltGui();
			Riivolution::SetDefault();
			Riivolution::Reload();
			ResumeGui();
			return MENU_RiivolutionMenu;
		}

		defaultBtn->ResetState();
	}

	return FlyingButtonsMenu::MainLoop();
}

void RiivolutionMenu::SetMainButton(int position, const char * ButtonText, GuiImageData * imageData, GuiImageData * RiivolutionImg)
{
	if(position >= (int) MainButton.size())
	{
		MainButtonImg.resize(position+1);
		MainButtonImgOver.resize(position+1);
		MainButtonTxt.resize(position+1);
		MainButton.resize(position+1);
	}

	MainButtonImg[position] = new GuiImage(imageData);
	MainButtonImgOver[position] = new GuiImage(RiivolutionImg);
	MainButtonImgOver[position]->SetScale(0.4);
	MainButtonImgOver[position]->SetPosition(50, -45);

	MainButtonTxt[position] = new GuiText(ButtonText, 18, ( GXColor ) {0, 0, 0, 255});
	MainButtonTxt[position]->SetAlignment(ALIGN_CENTER, ALIGN_TOP);
	MainButtonTxt[position]->SetPosition(0, 10);
	MainButtonTxt[position]->SetMaxWidth(imageData->GetWidth() - 10, DOTTED);

	MainButton[position] = new GuiButton(imageData->GetWidth(), imageData->GetHeight());
	MainButton[position]->SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	MainButton[position]->SetSoundOver(btnSoundOver);
	MainButton[position]->SetSoundClick(btnSoundClick);
	MainButton[position]->SetImage(MainButtonImg[position]);
	MainButton[position]->SetImageOver(MainButtonImg[position]);
	MainButton[position]->SetIcon(MainButtonImgOver[position]);
	MainButton[position]->SetLabel(MainButtonTxt[position]);
	MainButton[position]->SetTrigger(trigA);
	MainButton[position]->SetEffectGrow();

	switch(position % 4)
	{
		case 0:
			MainButton[position]->SetPosition(90, 75);
			break;
		case 1:
			MainButton[position]->SetPosition(340, 75);
			break;
		case 2:
			MainButton[position]->SetPosition(90, 230);
			break;
		case 3:
			MainButton[position]->SetPosition(340, 230);
			break;
		default:
			break;
	}
}

GuiImageData * RiivolutionMenu::GetImageData(int Riivolution)
{
	char filepath[300];
	snprintf(filepath, sizeof(filepath), "%sRiivolution_preview.png", RiivolutionList[Riivolution].ImageFolder.c_str());

	return (new GuiImageData(filepath));
}

void RiivolutionMenu::SetupMainButtons()
{
	RiivolutionList.clear();

	DirList RiivolutionDir(Settings.Riivolution_path, ".xml", DirList::Files);
	if (RiivolutionDir.GetFilecount() == 0)
	{
		WindowPrompt(tr( "No mods found." ), 0, "OK");
	}

	for(int i = 0; i < RiivolutionDir.GetFilecount(); ++i)
	{
		u8 *buffer = NULL;
		u32 filesize;
		gprintf("%i %s\n", i, RiivolutionDir.GetFilepath(i));
		LoadFileToMem(RiivolutionDir.GetFilepath(i), &buffer, &filesize);

		if(!buffer) continue;

		buffer[filesize-1] = '\0';

		int size = RiivolutionList.size();
		RiivolutionList.resize(size+1);

		RiivolutionList[size].Filepath = RiivolutionDir.GetFilepath(i);
		GetNodeText(buffer, "Riivolution-Title:", RiivolutionList[size].Title);
		GetNodeText(buffer, "Riivolution-Team:", RiivolutionList[size].Team);
		GetNodeText(buffer, "Riivolution-Version:", RiivolutionList[size].Version);
		GetNodeText(buffer, "Image-Folder:", RiivolutionList[size].ImageFolder);

		if(RiivolutionList[size].Title.size() == 0 && RiivolutionDir.GetFilename(i))
		{
			RiivolutionList[size].Title = RiivolutionDir.GetFilename(i);
			size_t pos = RiivolutionList[size].Title.rfind('.');
			if(pos != std::string::npos)
				RiivolutionList[size].Title.erase(pos);
		}

		if(RiivolutionList[size].ImageFolder.size() == 0)
		{
			RiivolutionList[size].ImageFolder = RiivolutionDir.GetFilepath(i);
			size_t pos = RiivolutionList[size].ImageFolder.rfind('.');
			if(pos != std::string::npos)
				RiivolutionList[size].ImageFolder.erase(pos);
			RiivolutionList[size].ImageFolder += '/';
		}
		else
		{
			std::string tempString = RiivolutionList[size].ImageFolder;
			RiivolutionList[size].ImageFolder = Settings.Riivolution_path;
			RiivolutionList[size].ImageFolder += tempString;
			RiivolutionList[size].ImageFolder += '/';
		}

		SetMainButton(size, RiivolutionList[size].Title.c_str(), MainButtonImgData, NULL);

		free(buffer);
	}
}

bool RiivolutionMenu::GetNodeText(const u8 *buffer, const char *node, std::string &outtext)
{
	const char * nodeText = strcasestr((const char *) buffer, node);
	if(!nodeText)
		return false;

	nodeText += strlen(node);

	while(*nodeText == ' ') nodeText++;

	while(*nodeText != '\0' && *nodeText != '\\' && *nodeText != '\n' && *nodeText != '"')
	{
		outtext.push_back(*nodeText);
		nodeText++;
	}

	return true;
}

void RiivolutionMenu::AddMainButtons()
{
	HaltGui();
	for(u32 i = 0; i < MainButton.size(); ++i)
		Remove(MainButton[i]);

	int FirstItem = currentPage*4;
	int n = 0;

	for(int i = FirstItem; i < (int) MainButton.size() && i < FirstItem+4; ++i)
	{
		delete RiivolutionPreviews[n];
		RiivolutionPreviews[n] = GetImageData(i);
		MainButtonImgOver[i]->SetImage(RiivolutionPreviews[n]);
		n++;
	}

	FlyingButtonsMenu::AddMainButtons();
}

void RiivolutionMenu::MainButtonClicked(int button)
{
	//! TODO: Clean me
	const char * title = RiivolutionList[button].Title.c_str();
	const char * author = RiivolutionList[button].Team.c_str();
	const char * version = RiivolutionList[button].Version.c_str();
	GuiImageData *thumbimageData = RiivolutionPreviews[button % 4];

	gprintf("\nRiivolution_Prompt(%s ,%s)", title, author);
	bool leave = false;

	GuiImageData btnOutline(Resources::GetFile("button_dialogue_box.png"), Resources::GetFileSize("button_dialogue_box.png"));
	GuiImageData dialogBox(Resources::GetFile("Riivolution_dialogue_box.png"), Resources::GetFileSize("Riivolution_dialogue_box.png"));

	GuiImage dialogBoxImg(&dialogBox);

	GuiWindow promptWindow(dialogBox.GetWidth(), dialogBox.GetHeight());
	promptWindow.SetAlignment(ALIGN_CENTER, ALIGN_MIDDLE);
	promptWindow.SetPosition(0, -10);

	GuiTrigger trigA;
	trigA.SetSimpleTrigger(-1, WPAD_BUTTON_A | WPAD_CLASSIC_BUTTON_A, PAD_BUTTON_A);
	GuiTrigger trigB;
	trigB.SetButtonOnlyTrigger(-1, WPAD_BUTTON_B | WPAD_CLASSIC_BUTTON_B, PAD_BUTTON_B);

	int PositionY = 30;

	GuiText titleTxt(tr( "Riivolution Title:" ), 18, thColor("r=0 g=0 b=0 a=255 - prompt windows text color"));
	titleTxt.SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	titleTxt.SetPosition(230, PositionY);
	PositionY += 20;

	GuiText titleTxt2(title, 18, thColor("r=0 g=0 b=0 a=255 - prompt windows text color"));
	titleTxt2.SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	titleTxt2.SetPosition(230, PositionY);
	titleTxt2.SetMaxWidth(dialogBox.GetWidth() - 220, WRAP);

	if(titleTxt2.GetTextWidth() >= dialogBox.GetWidth() - 220)
		PositionY += 50;
	else
		PositionY += 30;

	GuiText authorTxt(tr( "Author(s):" ), 18, thColor("r=0 g=0 b=0 a=255 - prompt windows text color"));
	authorTxt.SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	authorTxt.SetPosition(230, PositionY);
	PositionY += 20;

	GuiText authorTxt2(author, 18, thColor("r=0 g=0 b=0 a=255 - prompt windows text color"));
	authorTxt2.SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	authorTxt2.SetPosition(230, PositionY);
	authorTxt2.SetMaxWidth(dialogBox.GetWidth() - 220, DOTTED);

	if(authorTxt2.GetTextWidth() >= dialogBox.GetWidth() - 220)
		PositionY += 50;
	else
		PositionY += 30;

	GuiText versionTxt(tr( "Version:" ), 18, thColor("r=0 g=0 b=0 a=255 - prompt windows text color"));
	versionTxt.SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	versionTxt.SetPosition(230, PositionY);

	GuiText versionTxt2(version, 18, thColor("r=0 g=0 b=0 a=255 - prompt windows text color"));
	versionTxt2.SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	versionTxt2.SetPosition(235+versionTxt.GetTextWidth(), PositionY);
	versionTxt2.SetMaxWidth(dialogBox.GetWidth() - 220, DOTTED);

	GuiText applyBtnTxt(tr( "Apply" ), 22, thColor("r=0 g=0 b=0 a=255 - prompt windows button text color"));
	applyBtnTxt.SetMaxWidth(btnOutline.GetWidth() - 30);
	GuiImage applyBtnImg(&btnOutline);
	if (Settings.wsprompt)
	{
		applyBtnTxt.SetWidescreen(Settings.widescreen);
		applyBtnImg.SetWidescreen(Settings.widescreen);
	}
	GuiButton applyBtn(&applyBtnImg, &applyBtnImg, ALIGN_RIGHT, ALIGN_TOP, -5, 170, &trigA, btnSoundOver, btnSoundClick2, 1);
	applyBtn.SetLabel(&applyBtnTxt);
	applyBtn.SetScale(0.9);

	GuiText backBtnTxt(tr( "Back" ), 22, thColor("r=0 g=0 b=0 a=255 - prompt windows button text color"));
	backBtnTxt.SetMaxWidth(btnOutline.GetWidth() - 30);
	GuiImage backBtnImg(&btnOutline);
	if (Settings.wsprompt)
	{
		backBtnTxt.SetWidescreen(Settings.widescreen);
		backBtnImg.SetWidescreen(Settings.widescreen);
	}
	GuiButton backBtn(&backBtnImg, &backBtnImg, ALIGN_RIGHT, ALIGN_TOP, -5, 220, &trigA, btnSoundOver, btnSoundClick2, 1);
	backBtn.SetLabel(&backBtnTxt);
	backBtn.SetTrigger(&trigB);
	backBtn.SetScale(0.9);

	GuiImage RiivolutionImage(thumbimageData);
	RiivolutionImage.SetAlignment(ALIGN_LEFT, ALIGN_TOP);
	RiivolutionImage.SetPosition(20, 10);
	RiivolutionImage.SetScale(0.8);

	promptWindow.Append(&dialogBoxImg);
	promptWindow.Append(&RiivolutionImage);
	promptWindow.Append(&titleTxt);
	promptWindow.Append(&titleTxt2);
	promptWindow.Append(&authorTxt);
	promptWindow.Append(&authorTxt2);
	promptWindow.Append(&versionTxt);
	promptWindow.Append(&versionTxt2);
	promptWindow.Append(&applyBtn);
	promptWindow.Append(&backBtn);

	HaltGui();
	promptWindow.SetEffect(EFFECT_SLIDE_TOP | EFFECT_SLIDE_IN, 50);
	mainWindow->SetState(STATE_DISABLED);
	mainWindow->Append(&promptWindow);
	ResumeGui();

	while (!leave)
	{
		usleep(100);

		if (shutdown)
			Sys_Shutdown();
		else if (reset)
			Sys_Reboot();

		if (applyBtn.GetState() == STATE_CLICKED)
		{
			int choice = WindowPrompt(tr( "Do you want to apply this Mod ?" ), title, tr( "Yes" ), tr( "Cancel" ));
			if (choice)
			{
				if (Riivolution::Load(RiivolutionList[button].Filepath.c_str()))
				{
					snprintf(Settings.Riivolution, sizeof(Settings.Riivolution), RiivolutionList[button].Filepath.c_str());
					Riivolution::Reload();
					returnMenu = MENU_RiivolutionMENU;
					leave = true;
				}
			}
			mainWindow->SetState(STATE_DISABLED);
			promptWindow.SetState(STATE_DEFAULT);
			applyBtn.ResetState();
		}

		else if (backBtn.GetState() == STATE_CLICKED)
		{
			leave = true;
			backBtn.ResetState();
		}
	}

	promptWindow.SetEffect(EFFECT_SLIDE_TOP | EFFECT_SLIDE_OUT, 50);
	while (promptWindow.GetEffect() > 0) usleep(100);
	HaltGui();
	mainWindow->Remove(&promptWindow);
	mainWindow->SetState(STATE_DEFAULT);
	ResumeGui();
}
