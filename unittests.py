# -*- encoding: utf-8 -*-

import unittest
import pydawg

if pydawg.unicode:
	conv = lambda x: x
else:
	conv = lambda x: bytes(x, 'ascii')


class TestDAWGBase(unittest.TestCase):
	def setUp(self):
		self.D = pydawg.DAWG();
		self.words = "cat rat attribute tribute war warbute zaaa".split()

	def add_test_words(self):
		for word in sorted(self.words):
			self.assertTrue(self.D.add_word_unchecked(conv(word)))

		return self.D


class TestDAWG(TestDAWGBase):
	def test_add_word(self):
		D  = self.D
		w1 = "cat"

		D.add_word(conv(w1))
		D.add_word(conv(w1))	# adding the same word again is ok

		w2 = "catalog"
		D.add_word(conv(w2))	# ok 'catalog' > 'cat'

		w3 = "any"	# failure: 'any' < 'catalog'
		with self.assertRaises(ValueError):
			D.add_word(conv(w3))


	def test_close(self):
		D = self.add_test_words()

		D.close()	# now close
		with self.assertRaises(AttributeError):
			D.add_word(conv("won't work"))

		D.clear()	# clear, reset state
		D = self.add_test_words()


	def test_add_word_unchecked(self):
		self.add_test_words()

		if False:
			import dump2dot, os
			with open('1.dot', 'wt') as f:
				dump2dot.dump2dot(D, f)

			os.system("dotty 1.dot")


	def test_len(self):
		D = self.add_test_words()
		self.assertEqual(len(D), len(self.words))
	
	
	def test_clear(self):
		D = self.D

		self.assertEqual(len(D), 0)
		
		D = self.add_test_words()
		self.assertEqual(len(D), len(self.words))

		D.clear()
		self.assertEqual(len(D), 0)


	def test_exists(self):
		D = self.add_test_words()

		for word in self.words:
			self.assertTrue(D.exists(conv(word)))
			self.assertTrue(conv(word) in D);


		inexisting = "tree horse sky za at".split()
		for word in inexisting:
			self.assertFalse(D.exists(conv(word)))
			self.assertTrue(conv(word) not in D);


	def test_match(self):
		D = self.add_test_words()
		
		prefixes_true = "c r ra a at attr warb t tr".split()
		for word in prefixes_true:
			self.assertTrue(D.match(conv(word)))
		
		for word in self.words:
			self.assertTrue(D.match(conv(word)))
		
		prefixes_false = "hash yellow dark pinapple".split()
		for word in prefixes_false:
			self.assertFalse(D.match(conv(word)))
		
		self.assertFalse(D.match(conv("")))


	def test_longest_prefix(self):
		D = self.add_test_words()
		
		prefixes = "a at att attri attribu attribut attribute".split()
		for word in prefixes:
			self.assertEqual(D.longest_prefix(conv(word)), len(word))

		self.assertEqual(D.longest_prefix(conv("rating")), 3)	# "rat"
		self.assertEqual(D.longest_prefix(conv("")), 0)
		self.assertEqual(D.longest_prefix(conv("y")), 0)

	
	def test_words(self):
		D = self.add_test_words()

		I = map(conv, self.words)
		L = D.words()
		self.assertEqual(set(L), set(I))


	def test_words_utf8(self):
		words = u'dábale arroz a la zorra el abad'.split()
		for word in sorted(words):
			self.assertTrue(self.D.add_word(conv(word)))
		L = self.D.words()
		self.assertEqual(set(L), set(words))


	def test_iter(self):
		D = self.add_test_words()

		I = map(conv, self.words)
		L = set(D)
		self.assertEqual(set(L), set(I))

	
	def test_iter_invalidate(self):
		D = self.add_test_words()
		
		it = iter(D)
		w = next(it)
		
		D.clear()
		with self.assertRaises(ValueError):
			w = next(it)


	def findall_aux(self):
		D = self.D
		words = "abcde aXcde aZcdef aYc Xbcdefgh".split()
		for word in sorted(words):
			D.add_word(conv(word))


	def test_findall1(self):
		D = self.D
		self.findall_aux()

		L = [x for x in D.find_all(conv("a?c??"), conv("?"), pydawg.MATCH_EXACT_LENGTH)]
		I = map(conv, ["abcde", "aXcde"])
		self.assertEqual(set(I), set(L))


	def test_findall2(self):
		D = self.D
		self.findall_aux()

		L = [x for x in D.find_all(conv("a?c??"), conv("?"), pydawg.MATCH_AT_MOST_PREFIX)]
		I = map(conv, ["aYc", "abcde", "aXcde"])
		self.assertEqual(set(I), set(L))


	def test_findall3(self):
		D = self.D
		self.findall_aux()

		L = [x for x in D.find_all(conv("a?c??"), conv("?"), pydawg.MATCH_AT_LEAST_PREFIX)]
		I = I = map(conv, ["abcde", "aXcde", "aZcdef"])
		self.assertEqual(set(I), set(L))


	def test_get_stats(self):
		D = self.add_test_words()
		print(self.D.get_stats())
	
	
	def test_get_hash_stats(self):
		D = self.add_test_words()
		print(self.D.get_hash_stats())


class TestDumpLoad(TestDAWGBase):
	def test_dump(self):
		D = self.add_test_words();
		#print(D.bindump())


	def test_load(self):
		D = self.add_test_words()
		L = D.words()
		Ls = D.get_stats()

		dump = D.bindump()
		D.clear()
		D.binload(dump)
		N = D.words()
		Ns = D.get_stats()
		self.assertEqual(L, N)
		self.assertEqual(Ls, Ns)
		
		D.add_word(conv("zip"))
		D.add_word(conv("zzza"))
	

	def test_load_empty(self):
		D = self.D
		L = D.words()
		Ls = D.get_stats()

		dump = D.bindump()
		D.binload(dump)
		N = D.words()
		Ns = D.get_stats()
		self.assertEqual(L, N)
		self.assertEqual(Ls, Ns)

		D.add_word(conv("zip"))
		D.add_word(conv("zzza"))


	def test_load_constructor(self):
		D = self.add_test_words()
		L = D.words()
		Ls = D.get_stats()

		dump = D.bindump()
		D2 = pydawg.DAWG(dump)
		N = D2.words()
		Ns = D2.get_stats()
		self.assertEqual(L, N)
		self.assertEqual(Ls, Ns)

		D2.add_word(conv("zip"))
		D2.add_word(conv("zzza"))

class TestPickle(TestDAWGBase):
	def test_pickle_unpickle(self):
		import pickle

		D = self.add_test_words()
		dump = pickle.dumps(D)

		N = pickle.loads(dump)
		self.assertEqual(len(N), len(D))
		self.assertEqual(N.words(), D.words())


class TestMPH(TestDAWGBase):
	def test_word2index(self):
		if pydawg.perfect_hashing:
			D = self.D
			# empty
			for word in self.words:
				index = D.word2index(conv(word))
				self.assertEqual(index, None)

			D = self.add_test_words()

			S = set()
			for word in self.words:
				index = D.word2index(conv(word))
				S.add(index)

			# distinct numbers
			self.assertEqual(len(S), len(D))

			# indexes in range 1..len(D)
			self.assertEqual(min(S), 1)
			self.assertEqual(max(S), len(D))

			# inexising words
			index = D.word2index(conv("xyz"))
			self.assertEqual(index, None)
			index = D.word2index(conv(""))
			self.assertEqual(index, None)


	def test_index2word(self):
		if pydawg.perfect_hashing:
			D = self.D

			for i in range(-50, 50):
				word = D.index2word(i)
				self.assertEqual(word, None)
		
			D = self.add_test_words()

			def test(new_words=[]):
				S = set()
				for i in range(1, len(D) + 1):
					word = D.index2word(i)
					S.add(word)

				I = map(conv, self.words + new_words)
				self.assertEqual(S, set(I))

			# test 1st set
			test()

			word = "zebra"
			D.add_word(conv(word))

			# test 2nd set, after adding a word
			test([word])


# ------------------------------------------------------------------------

class DAWGSubclass1(pydawg.DAWG):

	def total(self):
		return len(self)

	def keys(self):
		return self.words()


class DAWGSubclass2(pydawg.DAWG):

	def __init__(self, param, *args):
		import sys;print("[subinit1]", end='', file=sys.stderr)
		self.param = param
		super(DAWGSubclass2, self).__init__(*args)
		import sys;print("[subinit2]", end='', file=sys.stderr)

	def total(self):
		return len(self)

	def keys(self):
		return self.words()


class TestSubclass1(TestDAWGBase):

	def setUp(self):
		self.D = DAWGSubclass1()
		self.words = "cat rat attribute tribute war warbute zaaa".split()
		for w in sorted(self.words):
			self.D.add_word(w)

	def tearDown(self):
		del self.D, self.words

	def test1_subclass(self):
		self.assertEqual(7, self.D.total())

	def test2_subclass(self):
		self.assertEqual(set(self.words), set(self.D.keys()))


class TestSubclass2(TestDAWGBase):

	def setUp(self):
		self.D = DAWGSubclass2('value')
		self.words = "cat rat attribute tribute war warbute zaaa".split()
		for w in sorted(self.words):
			self.D.add_word(w)

	def tearDown(self):
		del self.D, self.words

	def test1_subclass(self):
                self.assertEqual(7, self.D.total())

	def test2_subclass(self):
		self.assertEqual(set(self.words), set(self.D.keys()))

	def test3_subclass(self):
		self.assertEqual('value', self.D.param)

if __name__ == '__main__':
	unittest.main()
