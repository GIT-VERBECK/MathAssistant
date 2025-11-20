import './ErrorDisplay.css';

/**
 * Composant pour afficher les erreurs de manière user-friendly
 * @param {string} message - Message d'erreur à afficher
 * @param {function} onRetry - Fonction à appeler pour réessayer
 * @param {function} onDismiss - Fonction à appeler pour fermer l'erreur
 */
const ErrorDisplay = ({ message, onRetry, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="error-display">
      <div className="error-content">
        <div className="error-icon">⚠️</div>
        <div className="error-message">{message}</div>
        <div className="error-actions">
          {onRetry && (
            <button className="error-btn retry-btn" onClick={onRetry}>
              Réessayer
            </button>
          )}
          {onDismiss && (
            <button className="error-btn dismiss-btn" onClick={onDismiss}>
              Fermer
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorDisplay;

