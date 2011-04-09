"""
	This is part of pydawg Python module.

	Pure python implementation.

	Author    : Wojciech Muła, wojciech_mula@poczta.onet.pl
	WWW       : http://0x80.pl/proj/pydawg/
	License   : Public domain
	Date      : $Date$

	$Id$
"""


class DAWGNode:
	def __init__(self, char):
		self.children = {}
		self.parent = None
		self.final = False

	def get_next(self, char):
		try:
			return self.children[char]
		except KeyError:
			return None

	def set_next(self, char, child):
		self.children[char] = child
		child.parent = self

	def has_transition(self, char):
		return char in self.children

	def __str__(self):
		return "<" + "".join(self.children.keys()) + ">"


def equivalence(p, q):
	"check if states p and q are equivalent"

	if p.final != q.final:
		return False

	if len(p.children) != len(q.children):
		return False

	s = set(p.children)
	if s != set(q.children):
		return False

	"""
	# exact definition of equivalence
	for c in s:
		if not equivalence(p.children[c], q.children[c]):
				return False
	"""
	# pratical implementation - constraints make
	# this much simpler and faster
	for c in s:
		if p.children[c] != q.children[c]:
			return False

	return True


class DAWG:
	def __init__(self):
		self.register = set()
		self.q0 = DAWGNode(None);
		self.wp = ''

	def add_word(self, word):
		# 1. skip existing
		i = 0;
		s = self.q0
		while i < len(word) and s.has_transition(word[i]):
			s = s.get_next(word[i])
			i = i + 1

		assert s != None

		# 2. minimize
		if i < len(self.wp):
			self.repl_or_reg(s, self.wp[i:])


		# 3. add suffix
		while i < len(word):
			n = DAWGNode(word[i])
			s.set_next(word[i], n)
			assert n == s.get_next(word[i])
			s = n
			i = i + 1

		s.final = True
		self.wp = word


	def repl_or_reg(self, state, suffix):
		stack = []
		while suffix:
			letter = suffix[0]
			next   = state.get_next(letter)
			stack.append((state, letter, next))

			state = next
			suffix = suffix[1:]


		while stack:
			parent, letter, state = stack.pop()


			found = False
			for r in self.register:
				if equivalence(state, r):
					assert(parent.children[letter] == state)
					parent.children[letter] = r

					found = True
					break

			if not found:
				self.register.add(state)
			

	def freeze(self):
		self.repl_or_reg(self.q0, self.wp)


	def as_dot(self, file):

		nodes = set()
		edges = []
		tmp   = set()

		def aux(node):
			nodes.add((id(node), node.final))
			tmp.add(node)

			for letter, child in node.children.items():
				aux(child)

		aux(self.q0)

		for node in tmp:
			for letter, child in node.children.items():
				edges.append((id(node), letter, id(child)))

		import dump2dot
		dump2dot.dumpdata2dot(nodes, edges, file)


	def words(self):
		L = []
		def aux(node, word):
			if node.final:
				L.append(word)

			for letter, child in node.children.items():
				aux(child, word + letter)

		aux(self.q0, '')
		return L


import os

def main():
	words = "aimaient aimais aimait aime aiment".split()
	words = "cat rat attribute tribute".split()

	n = 1
	def dump():
		nonlocal n
		name = '%d.dot' % n
		with open(name, 'wt') as f:
			D.as_dot(f)

		n += 1
		return name

	D = DAWG()
	for word in sorted(words):
		print(word)
		D.add_word(word)
		#dump()

	D.freeze()
	name = dump()
	os.system("dotty %s" % name)

	print(words)
	print(D.words())


if __name__ == '__main__':
	main()
