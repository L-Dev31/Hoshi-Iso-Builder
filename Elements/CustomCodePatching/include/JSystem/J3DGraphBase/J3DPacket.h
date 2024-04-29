#pragma once

#include "JSystem/J3DGraphBase/J3DDrawBuffer.h"

const u32 sDifferedRegister[0x7] =
{
    0x1,
    0x2,
    0x1000000,
    0x10000000,
    0x20000000,
    0x2000000,
    0x8000000
};

const u32 sSizeOfDiffered[0x7] = 
{
    0xD,
    0x15,
    0x78,
    0x37,
    0xF,
    0x13,
    0x2D
};

class J3DShapePacket;

class J3DDisplayListObj
{
public:
    J3DDisplayListObj();

    u32 newDisplayList(u32);
    u32 newSingleDisplayList(u32);

    void swapBuffer();
    void callDL();
    void beginDL();
    u32 endDL();
    void beginPatch();
    u32 endPatch();

    void* mList; // _0
    u32 _4;
    u32 mListSize; // _8
    u32 _C;

    static u32 sInterruptFlag;
    static GDLObj sGDLObj;
};

class J3DPacket
{
public:
    virtual u32 entry(J3DDrawBuffer *);

    void addChildPacket(J3DPacket *);

    J3DPacket* mParent; // _4
    J3DPacket* mChild; // _8
};

class J3DDrawPacket : public J3DPacket
{
public:
    J3DDrawPacket();

    virtual void draw();
    virtual ~J3DDrawPacket();

    u32 newDisplayList(u32);
    u32 newSingleDisplayList(u32);

    u32 _C;
    u32 _10;
    u32 _14;
    u32 _18;
    u32 _1C;
    J3DDisplayListObj* mDLObj; // _20
    u32 _24;
};

class J3DMatPacket : public J3DDrawPacket
{
public:
    J3DMatPacket();

    virtual u32 entry(J3DDrawBuffer *);
    virtual void draw();
    virtual ~J3DMatPacket();

    void addShapePacket(J3DShapePacket *);
    void beginDiff();
    void endDiff();
    bool isSame(J3DMatPacket *) const;

    J3DMatPacket* _28;
    J3DShapePacket* mShapePacket; // _2C
    u32 _30;
    s32 _34;
    u32 _38;
    u32 _3C;
};

class J3DShapePacket : public J3DDrawPacket
{
public:
    J3DShapePacket();

    virtual u32 entry(J3DDrawBuffer *);
    virtual void draw();
    virtual ~J3DShapePacket();

    u8 _28[0x3C-0x28];
};