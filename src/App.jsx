import { useState, useRef, useEffect } from 'react'
import './App.css'
import LaTeXRenderer from './components/LaTeXRenderer'
import ErrorDisplay from './components/ErrorDisplay'
import { getLaTeXFromImage, analyzeImage } from './services/api'
import { generatePDFSimple } from './utils/pdfGenerator'

function App() {
  // États de navigation
  const [currentPage, setCurrentPage] = useState(0) // 0: Onboarding, 1: Capture, 2: Confirmation, 3: Loading, 4: Results, 5: About
  
  // États d'image
  const [capturedImage, setCapturedImage] = useState(null)
  const [showCamera, setShowCamera] = useState(false)
  const [cameraError, setCameraError] = useState(null)
  
  // États de traitement
  const [extractedLaTeX, setExtractedLaTeX] = useState(null)
  const [isExtractingLaTeX, setIsExtractingLaTeX] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')
  
  // États de résultats
  const [problemData, setProblemData] = useState(null)
  const [expandedSteps, setExpandedSteps] = useState(new Set([0])) // Étape 1 expandée par défaut
  
  // États d'erreur
  const [error, setError] = useState(null)
  
  // Refs
  const fileInputRef = useRef(null)
  const videoRef = useRef(null)
  const streamRef = useRef(null)

  // Navigation
  const handleNext = () => {
    if (currentPage === 0) {
      setCurrentPage(1)
    }
  }

  const handleSkip = () => {
    setCurrentPage(0)
    resetState()
  }

  const handleOpenAbout = () => {
    setCurrentPage(5)
  }

  const handleCloseAbout = () => {
    setCurrentPage(0)
  }

  // Gestion de l'image
  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      // Validation
      if (!file.type.startsWith('image/')) {
        setError('Veuillez sélectionner un fichier image valide.')
        return
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB
        setError('L\'image est trop grande. Veuillez utiliser une image de moins de 10MB.')
        return
      }
      
      const reader = new FileReader()
      reader.onloadend = () => {
        setCapturedImage(reader.result)
        setError(null)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const startCamera = async () => {
    try {
      setCameraError(null)
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' }
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        setShowCamera(true)
      }
    } catch (error) {
      console.error('Erreur d\'accès à la caméra:', error)
      setCameraError('Impossible d\'accéder à la caméra. Veuillez vérifier les permissions.')
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    setShowCamera(false)
    setCameraError(null)
  }

  const capturePhoto = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas')
      canvas.width = videoRef.current.videoWidth
      canvas.height = videoRef.current.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(videoRef.current, 0, 0)
      const imageData = canvas.toDataURL('image/png')
      setCapturedImage(imageData)
      stopCamera()
    }
  }

  const removeImage = () => {
    setCapturedImage(null)
    setExtractedLaTeX(null)
    setError(null)
  }

  // Extraction LaTeX
  const handleAnalyzeImage = async () => {
    if (!capturedImage) return
    
    setIsExtractingLaTeX(true)
    setLoadingMessage('Extraction LaTeX...')
    setError(null)
    
    try {
      const result = await getLaTeXFromImage(capturedImage)
      setExtractedLaTeX(result.latex)
      setCurrentPage(2) // Page de confirmation LaTeX
    } catch (err) {
      setError(err.message || 'Erreur lors de l\'extraction LaTeX')
    } finally {
      setIsExtractingLaTeX(false)
      setLoadingMessage('')
    }
  }

  // Confirmation et résolution
  const handleConfirmAndSolve = async () => {
    if (!capturedImage || !extractedLaTeX) return
    
    setIsAnalyzing(true)
    setLoadingMessage('Résolution du problème...')
    setCurrentPage(3) // Page de chargement
    setError(null)
    
    try {
      const result = await analyzeImage(capturedImage, extractedLaTeX)
      setProblemData(result)
      setLoadingMessage('Génération de l\'explication...')
      
      // Simuler un délai pour l'explication (sera remplacé par l'API réelle)
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setCurrentPage(4) // Page de résultats
    } catch (err) {
      setError(err.message || 'Erreur lors de l\'analyse')
      setCurrentPage(2) // Revenir à la page de confirmation
    } finally {
      setIsAnalyzing(false)
      setLoadingMessage('')
    }
  }

  const handleEditLaTeX = () => {
    setCurrentPage(1)
  }

  // Gestion des étapes
  const toggleStep = (index) => {
    const newExpanded = new Set(expandedSteps)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSteps(newExpanded)
  }

  // Export PDF
  const handleDownloadPDF = async () => {
    if (!problemData) return
    
    try {
      await generatePDFSimple({
        problem: problemData.problem,
        latex: problemData.latex,
        extractedLaTeX: extractedLaTeX,
        solution: problemData.solution,
        steps: problemData.steps || [],
        result: problemData.result,
        answer: problemData.answer,
      })
    } catch (error) {
      console.error('Erreur lors de la génération du PDF:', error);
      setError(`Erreur lors de la génération du PDF: ${error.message || 'Erreur inconnue'}`)
    }
  }

  // Reset complet
  const resetState = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    setShowCamera(false)
    setCapturedImage(null)
    setExtractedLaTeX(null)
    setProblemData(null)
    setError(null)
    setExpandedSteps(new Set([0]))
  }

  // Cleanup
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  return (
    <div className="home-page">
      {/* Header */}
      <header className="header">
        {currentPage === 0 && (
          <div className="menu-container">
            <button className="about-header-btn" onClick={handleOpenAbout}>
              À propos
            </button>
            <div className="menu-icon-container">
              <button className="menu-icon-btn" aria-label="Menu">
                ☰
              </button>
              <div className="menu-dropdown">
                <button className="menu-dropdown-btn" onClick={handleOpenAbout}>
                  À propos
                </button>
              </div>
            </div>
          </div>
        )}
        {currentPage === 1 && (
          <button className="back-header-btn" onClick={handleSkip}>
            ← Retour
          </button>
        )}
        {currentPage === 2 && (
          <button className="back-header-btn" onClick={handleEditLaTeX}>
            ← Modifier
          </button>
        )}
        {currentPage === 5 && (
          <button className="back-header-btn" onClick={handleCloseAbout}>
            ← Retour
          </button>
        )}
      </header>

      {/* Error Display */}
      {error && (
        <ErrorDisplay 
          message={error} 
          onRetry={() => setError(null)}
          onDismiss={() => setError(null)}
        />
      )}

      {/* Main Content */}
      <main className="main-content">
        {/* Page 0 - Onboarding */}
        {currentPage === 0 && (
          <>
            <div className="graphic-container">
              <svg 
                className="wavy-lines" 
                viewBox="0 0 200 120" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <path 
                  d="M 10 60 Q 30 20, 50 60 T 90 60 T 130 60 T 170 60 T 190 60" 
                  stroke="#1a4d7a" 
                  strokeWidth="3" 
                  fill="none"
                />
                <path 
                  d="M 10 60 Q 30 100, 50 60 T 90 60 T 130 60 T 170 60 T 190 60" 
                  stroke="#00a8ff" 
                  strokeWidth="3" 
                  fill="none"
                />
                <line x1="20" y1="100" x2="180" y2="100" stroke="#1a4d7a" strokeWidth="3" />
                <line x1="20" y1="110" x2="180" y2="110" stroke="#00a8ff" strokeWidth="3" />
              </svg>
              {/* <p className="graphic-text">Problème Complexe → Solution Simple</p> */}
            </div>

            <h1 className="headline">
              Math Assistant <br/> Votre guide Assistant IA 
            </h1>

            <p className="description">
              Prenez une photo de n'importe quel problème mathématique, de<br />
              l'algèbre simple au calcul complexe, et obtenez des<br />
              solutions instantanées étape par étape.
            </p>
         

            <div className="pagination">
              <span className="dot active"></span>
              <span className="dot"></span>
            </div>

            <button className="cta-button" onClick={handleNext}>Suivant</button>
          </>
        )}

        {/* Page 1 - Capture d'image */}
        {currentPage === 1 && (
          <>
            <div className="pagination-top">
              <span className="dot active"></span>
              <span className="dot"></span>
            </div>

            <div className="illustration-container">
              {capturedImage ? (
                <div className="image-preview-container">
                  <div className="image-preview-card">
                    <img src={capturedImage} alt="Problème mathématique capturé" className="captured-image" />
                    <button className="remove-image-btn" onClick={removeImage} aria-label="Supprimer l'image">
                      ×
                    </button>
                  </div>
                </div>
              ) : showCamera ? (
                <div className="camera-container">
                  <div className="camera-preview">
                    <video ref={videoRef} autoPlay playsInline className="camera-video"></video>
                    <button className="close-camera-btn" onClick={stopCamera} aria-label="Fermer l'appareil photo">
                      ×
                    </button>
                  </div>
                  <button className="capture-btn" onClick={capturePhoto}>
                  📹
                  </button>
                  {cameraError && <p className="camera-error">{cameraError}</p>}
                </div>
              ) : (
                <div className="illustration-card">
                  <svg 
                    className="camera-illustration" 
                    viewBox="0 0 300 250" 
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <g transform="translate(50, 80) rotate(-8)">
                      <rect x="0" y="0" width="80" height="100" rx="8" fill="white" />
                      <line x1="15" y1="25" x2="65" y2="25" stroke="#d0d0d0" strokeWidth="2" />
                      <line x1="15" y1="40" x2="65" y2="40" stroke="#d0d0d0" strokeWidth="2" />
                      <line x1="15" y1="55" x2="65" y2="55" stroke="#d0d0d0" strokeWidth="2" />
                      <line x1="15" y1="70" x2="65" y2="70" stroke="#d0d0d0" strokeWidth="2" />
                    </g>
                    <g transform="translate(120, 50)">
                      <rect x="0" y="0" width="100" height="180" rx="20" fill="none" stroke="#00a8ff" strokeWidth="4" />
                      <rect x="10" y="20" width="80" height="140" rx="8" fill="white" />
                      <rect x="20" y="30" width="60" height="75" rx="4" fill="white" />
                      <line x1="28" y1="42" x2="72" y2="42" stroke="#d0d0d0" strokeWidth="1.5" />
                      <line x1="28" y1="52" x2="72" y2="52" stroke="#d0d0d0" strokeWidth="1.5" />
                      <line x1="28" y1="62" x2="72" y2="62" stroke="#d0d0d0" strokeWidth="1.5" />
                      <line x1="28" y1="72" x2="72" y2="72" stroke="#d0d0d0" strokeWidth="1.5" />
                    </g>
                    <circle cx="200" cy="180" r="25" fill="#00a8ff" opacity="0.3" />
                    <circle cx="210" cy="190" r="20" fill="#00a8ff" opacity="0.4" />
                    <circle cx="220" cy="200" r="15" fill="#00a8ff" opacity="0.5" />
                  </svg>
                </div>
              )}
            </div>

            <h1 className="headline">Prenez une Photo, Obtenez la Réponse</h1>

            <p className="description">
              Utilisez votre appareil photo pour capturer n'importe quelle équation mathématique imprimée ou manuscrite. Notre IA la scannera et la résoudra en quelques secondes.
            </p>

            {!capturedImage && !showCamera && (
              <div className="action-buttons">
                <button className="action-btn upload-btn" onClick={handleUploadClick}>
                📰 Télécharger une Image
                </button>
                <button className="action-btn camera-btn" onClick={startCamera}>
                📹 Prendre une Photo
                </button>
              </div>
            )}

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*"
              style={{ display: 'none' }}
            />

            {capturedImage && (
              <button 
                className="cta-button" 
                onClick={handleAnalyzeImage}
                disabled={isExtractingLaTeX}
              >
                {isExtractingLaTeX ? 'Extraction...' : 'Analyser l\'Image'}
              </button>
            )}
          </>
        )}

        {/* Page 2 - Confirmation LaTeX */}
        {currentPage === 2 && (
          <div className="latex-confirmation-page">
            <h2 className="confirmation-title">Vérifiez l'équation détectée</h2>
            
            {capturedImage && (
              <div className="confirmation-image-container">
                <img src={capturedImage} alt="Original" className="confirmation-image" />
              </div>
            )}

            <div className="latex-preview-container">
              <p className="latex-label">Équation détectée :</p>
              <div className="latex-display">
                {extractedLaTeX ? (
                  <LaTeXRenderer latex={extractedLaTeX} />
                ) : (
                  <p>Aucune équation détectée</p>
                )}
              </div>
            </div>

            <div className="confirmation-actions">
              <button className="action-btn edit-btn" onClick={handleEditLaTeX}>
                Modifier
              </button>
              <button 
                className="cta-button" 
                onClick={handleConfirmAndSolve}
                disabled={isAnalyzing || !extractedLaTeX}
              >
                {isAnalyzing ? 'Résolution...' : 'Confirmer'}
              </button>
            </div>
          </div>
        )}

        {/* Page 3 - Chargement */}
        {currentPage === 3 && (
          <div className="loading-page">
            <div className="success-icon-container">
              <div className="success-icon">
                <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="50" cy="50" r="45" fill="#4CAF50" />
                  <path d="M 30 50 L 45 65 L 70 35" stroke="white" strokeWidth="6" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            </div>
            <h1 className="loading-title">Traitement en cours...</h1>
            <p className="loading-description">
              {loadingMessage || 'Analyse de votre problème mathématique...'}
            </p>
            <div className="pagination">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot active"></span>
            </div>
            <div className="loading-spinner"></div>
          </div>
        )}

        {/* Page 4 - Résultats */}
        {currentPage === 4 && problemData && (
          <div className="results-page">
            <header className="results-header">
              <button className="back-btn" onClick={() => setCurrentPage(1)}>
                ←
              </button>
              <h2 className="results-title">Demarche de Solution</h2>
              <button className="menu-btn" onClick={handleDownloadPDF} title="Télécharger PDF">
              📝
              </button>
            </header>

            <div className="results-content">
              <div className="problem-card">
                <p className="card-label">Equation Détectée</p>
                <div className="problem-equation-container">
                  <LaTeXRenderer latex={problemData.latex || extractedLaTeX || problemData.problem} />
                </div>
                {problemData.solution && (
                  <p className="problem-solution">Solution: {problemData.solution}</p>
                )}
                <div className="problem-icon"></div>
              </div>

              <h3 className="steps-heading">Demarche de Solution</h3>

              {problemData.steps && problemData.steps.length > 0 ? (
                problemData.steps.map((step, index) => (
                  <div 
                    key={index} 
                    className="step-card expanded step-card-visible"
                  >
                    <div className="step-header">
                      <div className="step-number active">
                        {index + 1}
                      </div>
                      <h4 className="step-title">{step.title || `Étape ${index + 1}`}</h4>
                    </div>
                    <div className="step-content">
                      {step.description && (
                        <p className="step-text">{step.description}</p>
                      )}
                      {step.formula && (
                        <div className="step-formula-container">
                          <LaTeXRenderer latex={step.formula} />
                        </div>
                      )}
                      {step.explanation && (
                        <p className="step-text">{step.explanation}</p>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="step-card expanded step-card-visible">
                  <div className="step-header">
                    <div className="step-number active">1</div>
                    <h4 className="step-title">Solution</h4>
                  </div>
                  <div className="step-content">
                    <p className="step-text">
                      {problemData.solution || 'Solution générée avec succès.'}
                    </p>
                  </div>
                </div>
              )}

              {/* Solution Finale */}
              {(() => {
                // Déterminer le résultat final à afficher
                let finalResult = null;
                const genericMessages = ['Résolution disponible', 'Solution générée avec succès', 'Solution disponible', 'Non disponible'];
                const originalEquation = problemData.latex || extractedLaTeX || problemData.problem || '';
                
                // Fonction pour normaliser une formule LaTeX pour comparaison
                const normalizeFormula = (str) => {
                  if (!str) return '';
                  return str
                    .replace(/\s+/g, '') // Retirer tous les espaces
                    .toLowerCase()
                    .trim();
                };
                
                // Fonction pour extraire la structure principale d'une formule (sans les valeurs numériques)
                const extractStructure = (formula) => {
                  if (!formula) return '';
                  return formula
                    .replace(/\d+/g, 'N') // Remplacer tous les nombres par 'N'
                    .replace(/\s+/g, '')
                    .toLowerCase();
                };
                
                // Fonction pour vérifier si une formule est un résultat calculé (différent de l'équation originale)
                const isCalculatedResult = (formula) => {
                  if (!formula || !originalEquation) return false;
                  
                  // Normaliser les deux formules pour comparaison
                  const normalizedFormula = normalizeFormula(formula);
                  const normalizedOriginal = normalizeFormula(originalEquation);
                  
                  // Si elles sont identiques, ce n'est pas un résultat calculé
                  if (normalizedFormula === normalizedOriginal) {
                    return false;
                  }
                  
                  // Vérifier si c'est juste une simplification (même structure, valeurs différentes)
                  const formulaStructure = extractStructure(formula);
                  const originalStructure = extractStructure(originalEquation);
                  
                  // Si les structures sont identiques, c'est juste une simplification, pas un résultat calculé
                  if (formulaStructure === originalStructure) {
                    return false;
                  }
                  
                  // Vérifier si la formule est très similaire à l'originale (plus de 85% de similarité)
                  // Si oui, c'est probablement juste une simplification
                  const minLength = Math.min(normalizedFormula.length, normalizedOriginal.length);
                  const maxLength = Math.max(normalizedFormula.length, normalizedOriginal.length);
                  
                  if (minLength > 0 && maxLength > 0) {
                    let matches = 0;
                    for (let i = 0; i < minLength; i++) {
                      if (normalizedFormula[i] === normalizedOriginal[i]) {
                        matches++;
                      }
                    }
                    const similarity = matches / maxLength;
                    if (similarity > 0.85) {
                      return false; // Plus de 85% de similarité = probablement juste une simplification
                    }
                  }
                  
                  // Si c'est un résultat numérique simple (pas de racines, fractions complexes, etc.), c'est un résultat calculé
                  if (isNumericResult(formula)) {
                    return true;
                  }
                  
                  // Si la formule est beaucoup plus courte que l'originale, c'est probablement un résultat calculé
                  if (normalizedFormula.length < normalizedOriginal.length * 0.7) {
                    return true;
                  }
                  
                  // Sinon, considérer comme résultat calculé seulement si vraiment différent
                  return true;
                };
                
                // Fonction pour vérifier si une formule contient un résultat numérique simple
                const isNumericResult = (formula) => {
                  if (!formula) return false;
                  // Vérifier si la formule est principalement numérique (pas d'opérations non résolues)
                  const hasUnresolvedOps = /[\^_\\]/.test(formula) || 
                                         formula.includes('sqrt') || 
                                         formula.includes('frac');
                  return !hasUnresolvedOps && /^[\d\s+\-*/=().]+$/.test(formula);
                };
                
                // 1. Vérifier si problemData a un champ result ou answer
                if (problemData.result) {
                  finalResult = problemData.result;
                } else if (problemData.answer) {
                  finalResult = problemData.answer;
                }
                // 2. Si la solution n'est pas un message générique, l'utiliser
                else if (problemData.solution && !genericMessages.some(msg => problemData.solution.includes(msg))) {
                  finalResult = problemData.solution;
                } 
                // 3. Chercher dans les étapes une formule qui est un résultat calculé
                else if (problemData.steps && problemData.steps.length > 0) {
                  // Chercher d'abord dans toutes les étapes une formule qui est différente de l'originale
                  for (let i = problemData.steps.length - 1; i >= 0; i--) {
                    const step = problemData.steps[i];
                    
                    // Vérifier les champs result ou answer de l'étape
                    if (step.result) {
                      finalResult = step.result;
                      break;
                    } else if (step.answer) {
                      finalResult = step.answer;
                      break;
                    }
                    
                    // Vérifier si la formule est un résultat calculé
                    if (step.formula && isCalculatedResult(step.formula)) {
                      // Si c'est un résultat numérique simple, l'utiliser
                      if (isNumericResult(step.formula)) {
                        finalResult = step.formula;
                        break;
                      }
                      // Sinon, vérifier si c'est la dernière étape avec une formule différente
                      if (i === problemData.steps.length - 1) {
                        finalResult = step.formula;
                        break;
                      }
                    }
                    
                    // Chercher dans l'explication un résultat final mentionné (ex: "obtenons 21" ou "= 21" ou "≈ 4.5528")
                    if (step.explanation) {
                      // Patterns plus larges pour trouver le résultat, y compris les approximations
                      const patterns = [
                        /(?:obtenons|donne|résultat|égal|=\s*|vaut|est\s+égal\s+à|≈|environ|approximativement)\s*(\d+(?:\.\d+)?)/i,
                        /=\s*(\d+(?:\.\d+)?)/,
                        /(\d+(?:\.\d+)?)\s*(?:est|vaut|donne)/i,
                        /(?:le\s+)?résultat\s+(?:est|vaut|donne|≈)\s+(\d+(?:\.\d+)?)/i,
                        /(?:pour\s+obtenir|on\s+obtient|on\s+trouve)\s+(?:environ|≈|approximativement)?\s*(\d+(?:\.\d+)?)/i
                      ];
                      
                      for (const pattern of patterns) {
                        const resultMatch = step.explanation.match(pattern);
                        if (resultMatch) {
                          finalResult = resultMatch[1];
                          break;
                        }
                      }
                      
                      if (finalResult) break;
                    }
                    
                    // Chercher aussi dans la description
                    if (step.description) {
                      const patterns = [
                        /(?:obtenons|donne|résultat|égal|=\s*|vaut|est\s+égal\s+à|≈|environ|approximativement)\s*(\d+(?:\.\d+)?)/i,
                        /=\s*(\d+(?:\.\d+)?)/,
                        /(\d+(?:\.\d+)?)\s*(?:est|vaut|donne)/i,
                        /(?:pour\s+obtenir|on\s+obtient|on\s+trouve)\s+(?:environ|≈|approximativement)?\s*(\d+(?:\.\d+)?)/i
                      ];
                      
                      for (const pattern of patterns) {
                        const resultMatch = step.description.match(pattern);
                        if (resultMatch) {
                          finalResult = resultMatch[1];
                          break;
                        }
                      }
                      
                      if (finalResult) break;
                    }
                  }
                  
                  // Si on n'a toujours pas trouvé, prendre la formule de la dernière étape
                  // MAIS seulement si elle est différente de l'équation originale
                  if (!finalResult) {
                    const lastStep = problemData.steps[problemData.steps.length - 1];
                    if (lastStep.formula && isCalculatedResult(lastStep.formula)) {
                      finalResult = lastStep.formula;
                    }
                  }
                }
                
                // Afficher le résultat final
                // Si on a un résultat et qu'il est différent de l'équation originale, l'afficher
                if (finalResult && isCalculatedResult(finalResult)) {
                  return (
                    <div className="final-solution-card">
                      <h4 className="final-solution-title">Résultat Final</h4>
                      <div className="final-solution-content">
                        {/* Essayer de détecter si la solution contient du LaTeX */}
                        {finalResult.includes('\\') || 
                         finalResult.includes('frac') || 
                         finalResult.includes('sqrt') ||
                         finalResult.includes('^') ||
                         finalResult.includes('_') ||
                         /[{}]/.test(finalResult) ? (
                          <div className="final-solution-formula">
                            <LaTeXRenderer latex={finalResult} />
                          </div>
                        ) : (
                          <p className="final-solution-text">{finalResult}</p>
                        )}
                      </div>
                    </div>
                  );
                }
                
                // Si on n'a pas de résultat calculé, ne rien afficher
                // (l'équation originale est déjà affichée dans la section "Equation Détectée")
                return null;
              })()}
            </div>

            <div className="bottom-nav">
              <button className="nav-btn download-pdf-btn" onClick={handleDownloadPDF}>
              📝 Télécharger PDF
              </button>
            </div>
          </div>
        )}

        {/* Page 5 - À propos */}
        {currentPage === 5 && (
          <div className="about-page">
            <div className="about-wrapper">
              <div className="about-header">
                <h1 className="about-title">À propos</h1>
              </div>

              <div className="about-info">
                
                <h2 className="creator-name">JEAN-MARC VERBECK</h2>
                <p className="creator-detail">Développeur Full Stack</p>
                <p className="creator-detail">🎓 ISIG-GOMA</p>
              </div>

              <p className="creator-bio-text">
                Passionné par le <strong>réseau informatique</strong>, la <strong>programmation web</strong> et les <strong>nouvelles technologies</strong>.
              </p>

              <div className="tech-list">
                <span className="tech-badge">React</span>
                <span className="tech-badge">FastAPI</span>
                <span className="tech-badge">OpenAI</span>
                <span className="tech-badge">WolframAlpha</span>
              </div>

              <p className="about-version">Version 1.0.0</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

