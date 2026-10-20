/**
 * Site rule: links to other websites open in a new tab and are marked with ↗ (class "extern",
 * styled in global.css). Applied at build time to all Markdown, so text typed in Pages CMS
 * follows the rule without editors having to think about it. Links to our own domain,
 * relative links, mailto: etc. are left alone.
 */
const OWN_HOSTS = new Set(['bronkhorsterkermis.nl', 'www.bronkhorsterkermis.nl']);

function isExternal(href) {
	if (typeof href !== 'string' || !/^https?:\/\//i.test(href)) return false;
	try {
		return !OWN_HOSTS.has(new URL(href).hostname.toLowerCase());
	} catch {
		return false;
	}
}

function visit(node, fn) {
	fn(node);
	if (node.children) for (const child of node.children) visit(child, fn);
}

export default function rehypeExternalLinks() {
	return (tree) => {
		visit(tree, (node) => {
			if (node.type !== 'element' || node.tagName !== 'a' || !isExternal(node.properties?.href)) return;
			node.properties.target = '_blank';
			node.properties.rel = ['noopener'];
			const cls = node.properties.className ?? [];
			node.properties.className = [...(Array.isArray(cls) ? cls : [cls]), 'extern'];
			node.children.push({
				type: 'element',
				tagName: 'span',
				properties: { className: ['sr-only'] },
				children: [{ type: 'text', value: ' (opent in een nieuw tabblad)' }],
			});
		});
	};
}
