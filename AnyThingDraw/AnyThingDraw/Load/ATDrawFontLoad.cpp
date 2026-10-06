#include "ATDrawFontLoad.h"

IDWriteFontCollectionLoader* ATDrawFontCollectionLoader::instance_(new(std::nothrow) ATDrawFontCollectionLoader());

ATDrawFontFileEnumerator::ATDrawFontFileEnumerator(IDWriteFactory* factory) :
	refCount_(0),
	factory_(SafeAcquire(factory)),
	currentFile_(),
	nextIndex_(0)
{
}

IDWriteFontFileLoader* ATDrawFontFileLoader::instance_(new(std::nothrow) ATDrawFontFileLoader());

HMODULE const ATDrawFontFileStream::moduleHandle_(GetCurrentModule());
HMODULE ATDrawFontFileStream::GetCurrentModule()
{
	HMODULE handle = NULL;

	GetModuleHandleEx(
		GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
		reinterpret_cast<LPCTSTR>(&GetCurrentModule),
		&handle
	);

	return handle;
}
ATDrawFontFileStream::ATDrawFontFileStream(UINT resourceID) :
	refCount_(0),
	resourcePtr_(NULL),
	resourceSize_(0)
{
	HRSRC resource = FindResourceW(moduleHandle_, MAKEINTRESOURCE(resourceID), L"TTF");
	if (resource != NULL)
	{
		HGLOBAL memHandle = LoadResource(moduleHandle_, resource);
		if (memHandle != NULL)
		{
			resourcePtr_ = LockResource(memHandle);
			if (resourcePtr_ != NULL)
			{
				resourceSize_ = SizeofResource(moduleHandle_, resource);
			}
		}
	}
}