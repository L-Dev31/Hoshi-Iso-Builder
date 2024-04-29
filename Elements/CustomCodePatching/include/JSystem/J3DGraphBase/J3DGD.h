#pragma once

#include "revolution.h"

void J3DGDSetTexImgPtrRaw(GXTexMapID, u32);
void J3DGDWriteCPCmd(u8, u32);

#ifdef __cplusplus
extern "C" {
#endif

u32 __GDLightID2Offset(s32);

#ifdef __cplusplus
}
#endif

void J3DGDWriteBPCmd(u32);
void J3DGDWrite_u32(u32);
void J3DGDWriteXFCmdHdr(u16, u8);
void J3DGDWrite_u16(u16);
