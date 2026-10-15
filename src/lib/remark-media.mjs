/**
 * Rewrites Markdown image URLs written by Pages CMS ("/media/...") to a path relative to the
 * Markdown file ("../../assets/media/..."), so Astro's image pipeline optimises them like any
 * other local image instead of expecting them in public/.
 */
import path from 'node:path';

const MEDIA_DIR = path.resolve('src/assets/media');

function visit(node, fn) {
	fn(node);
	if (node.children) for (const child of node.children) visit(child, fn);
}

export default function remarkMedia() {
	return (tree, file) => {
		const dir = path.dirname(file.path ?? file.history?.[0] ?? '');
		visit(tree, (node) => {
			if (node.type === 'image' && node.url?.startsWith('/media/')) {
				const target = path.join(MEDIA_DIR, decodeURI(node.url.slice('/media/'.length)));
				node.url = path.relative(dir, target).split(path.sep).join('/');
			}
		});
	};
}
