#include "ATDrawInputs.h"

#undef max
#undef min
#include "libcuckoo/cuckoohash_map.hh"

using DownMapType = libcuckoo::cuckoohash_map<BYTE, bool>;
static DownMapType* getDownMap()
{
	return reinterpret_cast<DownMapType*>(ATDrawInputs::downMap);
}

void* ATDrawInputs::downMap = new DownMapType;

void ATDrawInputs::SetKeyBoardDown(BYTE key, bool down)
{
	getDownMap()->insert_or_assign(key, down);
}
bool ATDrawInputs::IsKeyBoardDown(BYTE key)
{
	bool down = false;
	getDownMap()->find(key, down);
	return down;
}