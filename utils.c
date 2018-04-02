/*
	This is part of pydawg Python module.
	
	Helpers functions.
	This file is included directly.

	Author    : Wojciech Mu³a, wojciech_mula@poczta.onet.pl
	WWW       : http://0x80.pl/proj/pyahocorasick/
	License   : public domain
	Date      : $Date$

	$Id$
*/

#if PY_VERSION_HEX >=  0x03030000
# define NEW_UNICODE_API
#endif

#if (defined NEW_UNICODE_API && defined DAWG_UNICODE)
#  define STRING_FREE(obj) 	PyMem_Free(obj)
#  define STRING_RETURN_TYPE	DAWG_LETTER_TYPE
#else
#  define STRING_FREE(obj)	Py_DECREF(obj)
#  define STRING_RETURN_TYPE	PyObject
#endif


/* returns bytes or unicode internal buffer */
static STRING_RETURN_TYPE*
pymod_get_string(PyObject* obj, DAWG_LETTER_TYPE** word, size_t* wordlen) {
#if (defined NEW_UNICODE_API && defined DAWG_UNICODE)
	if (PyUnicode_READY(obj)) {
		PyErr_SetString(PyExc_TypeError, "string expected");
		return NULL;
	}
	//fprintf(stderr,"[KIND %d]",PyUnicode_KIND(obj));
	//*wordlen = PyUnicode_GET_LENGTH(obj);
	*word = (DAWG_LETTER_TYPE*)PyUnicode_AsWideCharString(obj, (ssize_t*)wordlen);
	return *word;
#elif defined DAWG_UNICODE
	if (PyUnicode_Check(obj)) {
		*word = (DAWG_LETTER_TYPE*)PyUnicode_AS_UNICODE(obj);
		*wordlen = (size_t)PyUnicode_GET_SIZE(obj);
		Py_INCREF(obj);
		return obj;
	}
	else {
		PyErr_SetString(PyExc_TypeError, "string expected");
		return NULL;
	}
#else
	if (PyBytes_Check(obj)) {
		*word = (uint8_t*)PyBytes_AS_STRING(obj);
		*wordlen = (size_t)PyBytes_GET_SIZE(obj);
		Py_INCREF(obj);
		return obj;
	}
	else {
		PyErr_SetString(PyExc_TypeError, "bytes expected");
		return NULL;
	}
#endif
}

