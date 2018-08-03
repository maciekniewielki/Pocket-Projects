from PIL import Image
import argparse
import numpy as np

class Charset:

	def __init__(self, chars=None, upper_bounds=None):
		if chars is None:
			chars = "@#$x+o,. "

		if not upper_bounds:
			n = len(chars)
			upper_bounds = np.linspace(1/n, 1., n)

		if len(chars) != len(upper_bounds):
			raise ValueError("upper_bounds size should match chars size.")
		self.upper_bounds = upper_bounds
		self.chars = chars

	def get_char(self, val):
		for char, bound in zip(self.chars, self.upper_bounds):
			if val <= bound:
				return char

		# In case the value is bigger than any upper bound
		return self.chars[-1]


class Translator:

	def __init__(self, input_filename, charset=None):
		self.input_filename = input_filename
		self._load()
		self.charset = charset

	def _load(self):
		self.im_data = np.array(Image.open(self.input_filename).convert("L")).transpose() / 255

	def translate(self, x_boxsize=3, y_boxsize=3):
		width, height = self.im_data.shape
		out_data = []
		for y in range(0, height, y_boxsize):
			for x in range(0, width, x_boxsize):
				box = self.im_data[x:x+x_boxsize, y:y+y_boxsize]
				char = self.translate_box(box)
				out_data.append(char)
			out_data.append("\n")
		return "".join(out_data)

	def translate_to_file(self, filename, x_boxsize=3, y_boxsize=3):
		with open(filename, "w") as f:
			f.write(self.translate(x_boxsize, y_boxsize))

	def translate_box(self, box):
		mean_val = np.mean(box)
		return self.charset.get_char(mean_val)


def parse_arguments():
	parser = argparse.ArgumentParser(description="Convert image file to ascii format.")

	parser.add_argument("-i", "--input-file", type=str, required=True, dest="input",
	 help="The input filename")
	
	parser.add_argument("-o", "--output-file", type=str, required=True, dest="output",
	 help="The output filename")

	parser.add_argument("-b", "--boxsize", type=int, default=3, dest="boxsize",
	 help="The size of pixel box per one character")
	
	parser.add_argument("--chars", type=str, dest="characters",
	 help="Set the charset used (in the ascending order of intensity, e.g. \"@x.\")")

	parser.add_argument("--upper-bounds", type=float, nargs="+", dest="upper_bounds",
	 help="List of upper bounds (normalized intensity values) where to use the next character. The default are equally spaced values from 0 (exclusive) to 1 (inclusive)")

	parser.add_argument("-c", "--correct", action="store_true", dest="correct",
	 help="Correct boxsize for height/width of ascii characters")

	parser.add_argument("-s", "--silent", action="store_true", dest="silent",
	 help="Do not output additional information to stdout")
	
	args = parser.parse_args()
	return args


SILENT = False
def log(text):
	if not SILENT:
		print(text)

def main():
	args = parse_arguments()
	if args.silent:
		global SILENT
		SILENT = True
	
	x_boxsize = y_boxsize = args.boxsize
	if args.correct:
		y_boxsize = x_boxsize * 2
		log("Corecting x_boxsize to %d" % x_boxsize)

	c = Charset(args.characters, args.upper_bounds)
	t = Translator(args.input, c)
	t.translate_to_file(args.output, x_boxsize, y_boxsize)



if __name__ == "__main__":
	main()