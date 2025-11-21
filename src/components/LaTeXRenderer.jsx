import { BlockMath, InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * Nettoie et prépare le LaTeX pour le rendu
 * @param {string} latex - La chaîne LaTeX brute
 * @returns {string} - LaTeX nettoyé
 */
const cleanLaTeX = (latex) => {
  if (!latex) return '';
  
  // Convertir en string et retirer les espaces superflus
  let cleaned = String(latex).trim();
  
  // Retirer les délimiteurs mathématiques si présents (KaTeX les ajoute automatiquement)
  if (cleaned.startsWith('$') && cleaned.endsWith('$')) {
    cleaned = cleaned.slice(1, -1).trim();
  }
  if (cleaned.startsWith('$$') && cleaned.endsWith('$$')) {
    cleaned = cleaned.slice(2, -2).trim();
  }
  if (cleaned.startsWith('\\[') && cleaned.endsWith('\\]')) {
    cleaned = cleaned.slice(2, -2).trim();
  }
  if (cleaned.startsWith('\\(') && cleaned.endsWith('\\)')) {
    cleaned = cleaned.slice(2, -2).trim();
  }
  
  // Décoder les entités HTML communes si présentes
  cleaned = cleaned
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
  
  return cleaned;
};

/**
 * Composant pour afficher des équations LaTeX
 * @param {string} latex - La chaîne LaTeX à afficher
 * @param {boolean} inline - Si true, affiche en ligne, sinon en bloc
 * @param {string} className - Classes CSS additionnelles
 */
const LaTeXRenderer = ({ latex, inline = false, className = '' }) => {
  if (!latex || String(latex).trim() === '') {
    return <span className={className}>Aucune équation détectée</span>;
  }

  // Nettoyer le LaTeX
  const cleanedLatex = cleanLaTeX(latex);

  // Si le LaTeX nettoyé est vide, afficher le message
  if (!cleanedLatex) {
    return <span className={className}>LaTeX vide</span>;
  }

  // Log pour déboguer (peut être retiré en production)
  if (process.env.NODE_ENV === 'development') {
    console.log('Rendu LaTeX:', { original: latex, cleaned: cleanedLatex, inline });
  }

  // react-katex gère automatiquement les erreurs de parsing
  // et affiche un message d'erreur dans le DOM si le LaTeX est invalide
  try {
    if (inline) {
      return <InlineMath math={cleanedLatex} className={className} errorColor="#cc0000" />;
    } else {
      return <BlockMath math={cleanedLatex} className={className} errorColor="#cc0000" />;
    }
  } catch (error) {
    // Fallback en cas d'erreur JavaScript (ne devrait normalement pas arriver)
    console.error('Erreur de rendu LaTeX:', error, 'LaTeX original:', latex, 'LaTeX nettoyé:', cleanedLatex);
    return (
      <div className={`latex-error ${className}`} style={{ 
        padding: '1rem', 
        backgroundColor: '#fff3cd', 
        border: '1px solid #ffc107',
        borderRadius: '4px',
        margin: '0.5rem 0'
      }}>
        <p style={{ margin: '0 0 0.5rem 0', fontWeight: 'bold', color: '#856404' }}>
          Erreur de rendu LaTeX:
        </p>
        <code style={{ 
          display: 'block', 
          whiteSpace: 'pre-wrap', 
          wordBreak: 'break-all',
          color: '#856404'
        }}>
          {latex}
        </code>
      </div>
    );
  }
};

export default LaTeXRenderer;

