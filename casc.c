#define PY_SSIZE_T_CLEAN
// #define Py_LIMITED_API 0x03030000
#include <Python.h>
#include <CascLib.h>

PyObject* casc_open(PyObject* self, PyObject* args) {
	const char* path = "";
	wchar_t widepath[MAX_PATH] = { 0 };
	void* storage = NULL;

	if (!PyArg_ParseTuple(args, "s", &path)) {
		PyErr_SetString(PyExc_TypeError, "Parameter must be a string");
		return NULL;
	}

	mbstowcs(widepath, path, strlen(path));

	if(!CascOpenStorage(widepath, 0, &storage)) {
		char err[0x100] = {0};
		sprintf(err, "Problem opening archive: %d", GetCascError());
		PyErr_SetString(PyExc_OSError, err);
		CascCloseStorage(storage);
		return NULL;
	}

	return Py_BuildValue ("K", storage);
}

PyObject* casc_close(PyObject* self, PyObject* args) {
	void* storage = NULL;

	if (!PyArg_ParseTuple(args, "K", &storage)) {
		PyErr_SetString(PyExc_TypeError, "Parameter must be a casc store object.");
		return NULL;
	}

	if(!CascCloseStorage(storage)) {
		PyErr_SetString(PyExc_TypeError, "Failed to close the store.");
		return NULL;

	}

	Py_RETURN_NONE;
}

PyObject* casc_find_first_file(PyObject* self, PyObject* args) {
	void* storage = NULL;
	CASC_FIND_DATA data = { 0 };
	const char* path = "";
	wchar_t widepath[MAX_PATH] = { 0 };
	
	if (!PyArg_ParseTuple(args, "Ks", &storage, &path)) {
		PyErr_SetString(PyExc_TypeError, "Wrong parameters.");
		return NULL;
	}
	mbstowcs(widepath, path, strlen(path));

	void* handle = CascFindFirstFile(storage, widepath, &data, L"");

	return Py_BuildValue("(K,{s:s,s:i,s:i})", handle, "filename", data.szFileName, "file_size", data.FileSize, "exists_locally", data.bFileAvailable);
}

PyObject* casc_find_next_file(PyObject* self, PyObject* args) {
	void* handle = NULL;
	CASC_FIND_DATA data = { 0 };

	if (!PyArg_ParseTuple(args, "K", &handle)) {
		PyErr_SetString(PyExc_TypeError, "Parameter must be a casc store object.");
		return NULL;
	}
	
	bool result = CascFindNextFile(handle, &data);

	if (result) {
		return Py_BuildValue("(K,{s:s,s:i,s:i})", handle, "filename", data.szFileName, "file_size", data.FileSize, "exists_locally", data.bFileAvailable);
	} else {
		CascFindClose(handle);
		Py_INCREF(Py_None);
		return Py_BuildValue("(O,{})", Py_None);
	}
}

PyObject* casc_find_close(PyObject* self, PyObject* args) {
	void* handle = NULL;

	if (!PyArg_ParseTuple(args, "K", &handle)) {
		PyErr_SetString(PyExc_TypeError, "Parameter must be a casc store object.");
		return NULL;
	}
	
	if(CascFindClose(handle)) {
		Py_RETURN_NONE;
	} else {
		PyErr_SetString(PyExc_TypeError, "Failed close find.");
		return NULL;
	}
}

PyObject* casc_open_file(PyObject* self, PyObject* args) {
	void* storage = NULL;
	const char* path = "";
	wchar_t widepath[MAX_PATH] = { 0 };
	void* file_ptr = NULL;

	if (!PyArg_ParseTuple(args, "Ks", &storage, &path)) {
		PyErr_SetString(PyExc_TypeError, "Wrong parameters.");
		return NULL;
	}

	mbstowcs(widepath, path, strlen(path));

	if(CascOpenFile(storage, path, 0, CASC_OPEN_BY_NAME, &file_ptr)) {
		Py_INCREF(Py_True);
		return Py_BuildValue("(OK)", Py_True, file_ptr);
	} else {
		CascCloseFile(file_ptr);
		Py_INCREF(Py_False);
		return Py_BuildValue("(OK)", Py_False, GetCascError());
	}
}

PyObject* casc_read_file(PyObject* self, PyObject* args) {
	void* handle = NULL;
	Py_ssize_t size = 0;
	Py_ssize_t actually_read = 0;

	if (!PyArg_ParseTuple(args, "K", &handle)) {
		PyErr_SetString(PyExc_TypeError, "Parameter must be a file reference.");
		return NULL;
	}
	if(CascGetFileSize64(handle, &size) == CASC_INVALID_SIZE) {
		CascCloseFile(handle);
		PyErr_SetString(PyExc_ValueError, "Couldn't get the size of the file.");
		return NULL;
	}
	char* buffer = malloc(size);
	PyObject* rv = NULL;
	if(CascReadFile(handle, buffer, size, &actually_read)) {
		rv = Py_BuildValue("Ky#K", handle, buffer, size, actually_read);
	} else {
		Py_INCREF(Py_None);
		rv = Py_BuildValue("KOK", handle, Py_None, 0);
	}
	free(buffer);
	return rv;
}

PyObject* casc_close_file(PyObject* self, PyObject* args) {
	void* handle = NULL;

	if (!PyArg_ParseTuple(args, "K", &handle)) {
		PyErr_SetString(PyExc_TypeError, "Parameter must be a file reference.");
		return NULL;
	}

	if(!CascCloseFile(handle)) {
		PyErr_SetString(PyExc_TypeError, "Failed close file.");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyMethodDef CascMethods[] = {
	{"open", casc_open, METH_VARARGS, "Opens a CASC repository."},
	{"close", casc_close, METH_VARARGS, "Closes a CASC repository."},

	{"find_first_file", casc_find_first_file, METH_VARARGS, "Finds the first file matching a pattern."},
	{"find_next_file", casc_find_next_file, METH_VARARGS, "Finds the next file matching a pattern from "
	"a previous casc_find_first_file or casc_find_next_file call."},
	{"find_close", casc_find_close, METH_VARARGS, "Finds the next file matching a pattern from "},
	
	{"open_file", casc_open_file, METH_VARARGS, "Opens a file."},
	{"read_file", casc_read_file, METH_VARARGS, "Returns the content of a file."},
	{"close_file", casc_close_file, METH_VARARGS, "Closes a file."},
	{NULL, NULL, 0, NULL},
};

static struct PyModuleDef cascmodule = {
	PyModuleDef_HEAD_INIT,
	"casc",
	NULL,
	-1,
	CascMethods,
};

PyMODINIT_FUNC
PyInit__casc(void)
{
	return PyModule_Create(&cascmodule);
}
