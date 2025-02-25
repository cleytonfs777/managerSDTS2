import adapter from '@sveltejs/adapter-auto';
import path from 'path'; // ✅ Importando o módulo 'path'
import { fileURLToPath } from 'url';

// ✅ Corrigindo __dirname para funcionar no ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		alias: {
			$lib: path.resolve(__dirname, 'src/lib')  // ✅ Garantindo caminho absoluto correto
		},
		adapter: adapter()
	}
};

export default config;
