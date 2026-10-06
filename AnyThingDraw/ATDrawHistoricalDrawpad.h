#pragma once
#include "ATDrawMain.h"


extern int current_record_pointer, total_record_pointer;
extern int reference_record_pointer, practical_total_record_pointer;
extern Json::Value record_value;

//载入记录
//保存图像到指定目录

// 撤回操作
void ATDrawRecall();
