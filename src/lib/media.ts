/**
 * Content refers to images by their CMS path, e.g. "/media/jaren/2025/foto.jpg" (Pages CMS writes
 * that "output" path). The files live in src/assets/media so Astro can resize them; this maps the
 * CMS path to the imported image.
 */
import type { ImageMetadata } from 'astro';

const files = import.meta.glob<{ default: ImageMetadata }>(
	'/src/assets/media/**/*.{jpg,jpeg,png,gif,webp,avif,JPG,JPEG,PNG}',
	{ eager: true },
);

export function media(path: string): ImageMetadata {
	const key = '/src/assets' + decodeURI(path);
	const file = files[key];
	if (!file) throw new Error(`Afbeelding niet gevonden: ${path} (verwacht in src/assets${path})`);
	return file.default;
}
