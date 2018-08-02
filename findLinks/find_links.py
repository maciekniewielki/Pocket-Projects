import requests
import argparse
from bs4 import BeautifulSoup


def parse_arguments():
	parser = argparse.ArgumentParser(description="Find hyperlinks on a given page.")

	parser.add_argument("page", type=str, help="The link to the page.")
	parser.add_argument("-min", "--minimum-depth", type=int, dest="min_depth", default=0, help="Minimum depth in the html tree (inclusive)")
	parser.add_argument("-max", "--maximum-depth", type=int, dest="max_depth", default=999, help="Maximum depth in the html tree (inclusive)")
	parser.add_argument("-e", "--extension", type=str, dest="ext", default=[""], nargs="+", help="Display only links with this extension (e.g. \".mp4\"). You can supply more than one extension")
	
	args = parser.parse_args()
	return args


def check_depth(tag):
	depth = 0
	while tag.parent is not None:
		tag = tag.parent
		depth += 1
	return depth

def endswith_any_extension(name, extensions):
	for ext in extensions:
		if name.endswith(ext):
			return True

	return False


def main():
	args = parse_arguments()

	content = requests.get(args.page)
	soup = BeautifulSoup(content.text, 'html.parser')

	for link in soup.find_all("a"):
		if link.has_attr('href'):
			if endswith_any_extension(link['href'], args.ext) and args.min_depth <= check_depth(link) <= args.max_depth:
				print(link["href"])

if __name__ == "__main__":
	main()
