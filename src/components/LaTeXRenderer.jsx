import { BlockMath, InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * Composant pour afficher des équations LaTeX
 * @param {string} latex - La chaîne LaTeX à afficher
 * @param {boolean} inline - Si true, affiche en ligne, sinon en bloc
 * @param {string} className - Classes CSS additionnelles
 */
const LaTeXRenderer = ({ latex, inline = false, className = '' }) => {
  if (!latex || latex.trim() === '') {
    return <span className={className}>Aucune équation détectée</span>;
  }

  try {
    if (inline) {
      return <InlineMath math={latex} className={className} />;
    } else {
      return <BlockMath math={latex} className={className} />;
    }
  } catch (error) {
    console.error('Erreur de rendu LaTeX:', error);
    return (
      <div className={`latex-error ${className}`}>
        <p>Erreur de rendu LaTeX:</p>
        <code>{latex}</code>
      </div>
    );
  }
};

export default LaTeXRenderer;

