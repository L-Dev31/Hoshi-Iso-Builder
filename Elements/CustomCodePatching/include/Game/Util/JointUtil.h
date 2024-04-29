#pragma once

#include "revolution.h"
#include "JSystem.h"

class J3DModel;
class J3DModelData;
class J3DJoint;
class LiveActor;

namespace MR {
    J3DJoint* getJoint(J3DModel *, const char *);
    J3DJoint* getJoint(const LiveActor *, const char *);
    J3DJoint* getJoint(const LiveActor *, u16);
    MtxPtr getJointMtx(J3DModel *, const char *);
    MtxPtr getJointMtx(const LiveActor *, const char *);
    MtxPtr getJointMtx(const LiveActor *, s32);

    s16 getJointIndex(const LiveActor *, const char *);
    const char* getJointName(const LiveActor *, s32);
    s16 getJointNum(const LiveActor *);
    bool isExistJoint(const LiveActor *, const char *);
    void copyJointPos(J3DModel *, const char *, TVec3f *);
    void copyJointPos(const LiveActor *, const char *, TVec3f *);
    void copyJointPos(J3DModel *, int, TVec3f *);
    void copyJointPos(const LiveActor *, int, TVec3f *);
    void copyJointScale(const LiveActor *, const char *, TVec3f *);
    void hideJoint(J3DJoint *);
    void hideJoint(J3DModel *, const char *);
    void hideJoint(const LiveActor *, const char *);
    void hideJointAndChildren(J3DJoint *);
    void hideJointAndChildren(J3DModel *, const char *);
    void hideJointAndChildren(const LiveActor *, const char *);
    void showJoint(J3DJoint *);
    void showJoint(J3DModel *, const char *);
    void showJoint(const LiveActor *, const char *);
    void showJointAndChildren(J3DJoint *);
    void showJointAndChildren(J3DModel *, const char *);
    void showJointAndChildren(const LiveActor *, const char *);
    s16 searchChildJoint(J3DJoint *, J3DJoint *);
    s16 getParentJoint(J3DModelData *, J3DJoint *);
    s16 getParentJoint(const LiveActor *, J3DJoint *);
};
