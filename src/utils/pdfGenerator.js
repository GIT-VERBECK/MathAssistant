import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import katex from 'katex';
import 'katex/dist/katex.min.css';

/**
 * Calcule le résultat final à partir des données (même logique que dans App.jsx)
 */
const calculateFinalResult = (data, originalEquation) => {
  let finalResult = null;
  const genericMessages = ['Résolution disponible', 'Solution générée avec succès', 'Solution disponible', 'Non disponible'];
  
  // Fonction pour normaliser une formule LaTeX pour comparaison
  const normalizeFormula = (str) => {
    if (!str) return '';
    return str.replace(/\s+/g, '').toLowerCase().trim();
  };
  
  // Fonction pour extraire la structure principale d'une formule
  const extractStructure = (formula) => {
    if (!formula) return '';
    return formula.replace(/\d+/g, 'N').replace(/\s+/g, '').toLowerCase();
  };
  
  // Fonction pour vérifier si une formule contient un résultat numérique simple
  const isNumericResult = (formula) => {
    if (!formula) return false;
    const hasUnresolvedOps = /[\^_\\]/.test(formula) || 
                           formula.includes('sqrt') || 
                           formula.includes('frac');
    return !hasUnresolvedOps && /^[\d\s+\-*/=().]+$/.test(formula);
  };
  
  // Fonction pour vérifier si une formule est un résultat calculé
  const isCalculatedResult = (formula) => {
    if (!formula || !originalEquation) return false;
    
    const normalizedFormula = normalizeFormula(formula);
    const normalizedOriginal = normalizeFormula(originalEquation);
    
    if (normalizedFormula === normalizedOriginal) return false;
    
    const formulaStructure = extractStructure(formula);
    const originalStructure = extractStructure(originalEquation);
    
    if (formulaStructure === originalStructure) return false;
    
    const minLength = Math.min(normalizedFormula.length, normalizedOriginal.length);
    const maxLength = Math.max(normalizedFormula.length, normalizedOriginal.length);
    
    if (minLength > 0 && maxLength > 0) {
      let matches = 0;
      for (let i = 0; i < minLength; i++) {
        if (normalizedFormula[i] === normalizedOriginal[i]) matches++;
      }
      const similarity = matches / maxLength;
      if (similarity > 0.85) return false;
    }
    
    if (isNumericResult(formula)) return true;
    if (normalizedFormula.length < normalizedOriginal.length * 0.7) return true;
    
    return true;
  };
  
  // 1. Vérifier si data a un champ result ou answer
  if (data.result) {
    finalResult = data.result;
  } else if (data.answer) {
    finalResult = data.answer;
  }
  // 2. Si la solution n'est pas un message générique, l'utiliser
  else if (data.solution && !genericMessages.some(msg => data.solution.includes(msg))) {
    finalResult = data.solution;
  }
  // 3. Chercher dans les étapes
  else if (data.steps && data.steps.length > 0) {
    // PRIORITÉ 1: Chercher d'abord la formule de la dernière étape si elle est vraiment calculée
    const lastStep = data.steps[data.steps.length - 1];
    if (lastStep.formula && isCalculatedResult(lastStep.formula)) {
      // Si c'est un résultat numérique simple, l'utiliser
      if (isNumericResult(lastStep.formula)) {
        finalResult = lastStep.formula;
      } else {
        // Sinon, utiliser la formule de la dernière étape
        finalResult = lastStep.formula;
      }
    }
    
    // PRIORITÉ 2: Si pas de formule valide dans la dernière étape, chercher dans toutes les étapes
    if (!finalResult) {
      for (let i = data.steps.length - 1; i >= 0; i--) {
        const step = data.steps[i];
        
        if (step.result) {
          finalResult = step.result;
          break;
        } else if (step.answer) {
          finalResult = step.answer;
          break;
        }
        
        // Chercher une formule vraiment calculée
        if (step.formula && isCalculatedResult(step.formula)) {
          if (isNumericResult(step.formula)) {
            finalResult = step.formula;
            break;
          }
        }
      }
    }
    
    // PRIORITÉ 3: Chercher une valeur numérique dans la DERNIÈRE étape seulement (pour éviter les résultats intermédiaires)
    if (!finalResult && lastStep) {
      // Chercher dans l'explication de la dernière étape
      if (lastStep.explanation) {
        const patterns = [
          /(?:résultat\s+final|résultat|obtenons|donne|égal|=\s*|vaut|est\s+égal\s+à|≈|environ|approximativement)\s*(\d+(?:\.\d+)?)/i,
          /(?:le\s+)?résultat\s+(?:final|est|vaut|donne|≈)\s+(\d+(?:\.\d+)?)/i,
          /(?:pour\s+obtenir|on\s+obtient|on\s+trouve)\s+(?:le\s+)?résultat\s+(?:final|est|vaut|donne|≈|environ|approximativement)?\s*(\d+(?:\.\d+)?)/i
        ];
        
        for (const pattern of patterns) {
          const resultMatch = lastStep.explanation.match(pattern);
          if (resultMatch) {
            finalResult = resultMatch[1];
            break;
          }
        }
      }
      
      // Chercher dans la description de la dernière étape
      if (!finalResult && lastStep.description) {
        const patterns = [
          /(?:résultat\s+final|résultat|obtenons|donne|égal|=\s*|vaut|est\s+égal\s+à|≈|environ|approximativement)\s*(\d+(?:\.\d+)?)/i,
          /(?:le\s+)?résultat\s+(?:final|est|vaut|donne|≈)\s+(\d+(?:\.\d+)?)/i
        ];
        
        for (const pattern of patterns) {
          const resultMatch = lastStep.description.match(pattern);
          if (resultMatch) {
            finalResult = resultMatch[1];
            break;
          }
        }
      }
    }
  }
  
  return finalResult && isCalculatedResult(finalResult) ? finalResult : null;
};

/**
 * Trouve la position de l'accolade fermante correspondante
 */
const findMatchingBrace = (str, startPos) => {
  let depth = 1;
  let pos = startPos + 1;
  while (pos < str.length && depth > 0) {
    if (str[pos] === '{') depth++;
    else if (str[pos] === '}') depth--;
    pos++;
  }
  return depth === 0 ? pos - 1 : -1;
};

/**
 * Convertit une formule LaTeX en texte plus lisible pour le PDF
 * Gère les expressions imbriquées de manière récursive
 */
const latexToReadableText = (latex) => {
  if (!latex) return '';
  
  let text = String(latex);
  
  // Fonction récursive pour traiter les expressions imbriquées
  const processNested = (str, depth = 0) => {
    if (depth > 10) return str; // Protection contre la récursion infinie
    if (!str) return str;
    
    // Traiter les racines carrées (doit être fait AVANT les fractions car elles peuvent être imbriquées)
    let changed = true;
    let iterations = 0;
    while (changed && iterations < 50) {
      changed = false;
      iterations++;
      const sqrtIndex = str.indexOf('\\sqrt{');
      if (sqrtIndex !== -1) {
        const braceStart = sqrtIndex + 6;
        const braceEnd = findMatchingBrace(str, braceStart);
        if (braceEnd !== -1 && braceEnd > braceStart) {
          const content = str.substring(braceStart + 1, braceEnd);
          const processed = processNested(content, depth + 1);
          // Utiliser "sqrt" au lieu de √ pour une meilleure compatibilité PDF
          const replacement = `sqrt(${processed})`;
          str = str.substring(0, sqrtIndex) + replacement + str.substring(braceEnd + 1);
          changed = true;
        }
      }
    }
    
    // Traiter les racines n-ièmes
    let pos = 0;
    while ((pos = str.indexOf('\\sqrt[', pos)) !== -1) {
      const bracketEnd = str.indexOf(']', pos + 6);
      if (bracketEnd !== -1) {
        const n = str.substring(pos + 6, bracketEnd);
        const braceStart = bracketEnd + 1;
        if (str[braceStart] === '{') {
          const braceEnd = findMatchingBrace(str, braceStart);
          if (braceEnd !== -1) {
            const content = str.substring(braceStart + 1, braceEnd);
            const processed = processNested(content, depth + 1);
            const replacement = `sqrt[${n}](${processed})`;
            str = str.substring(0, pos) + replacement + str.substring(braceEnd + 1);
            pos += replacement.length;
          } else {
            pos++;
          }
        } else {
          pos++;
        }
      } else {
        pos++;
      }
    }
    
    // Traiter les fractions (après les racines carrées)
    changed = true;
    iterations = 0;
    while (changed && iterations < 50) {
      changed = false;
      iterations++;
      const fracIndex = str.indexOf('\\frac{');
      if (fracIndex !== -1) {
        const numStart = fracIndex + 6;
        const numEnd = findMatchingBrace(str, numStart);
        if (numEnd !== -1 && str[numEnd + 1] === '{') {
          const denStart = numEnd + 1;
          const denEnd = findMatchingBrace(str, denStart);
          if (denEnd !== -1 && denEnd > denStart) {
            const num = str.substring(numStart + 1, numEnd);
            const den = str.substring(denStart + 1, denEnd);
            const processedNum = processNested(num, depth + 1);
            const processedDen = processNested(den, depth + 1);
            const numSimple = /^[\d\w\s+\-*/=()]+$/.test(processedNum);
            const denSimple = /^[\d\w\s+\-*/=()]+$/.test(processedDen);
            const numPart = numSimple ? processedNum : `(${processedNum})`;
            const denPart = denSimple ? processedDen : `(${processedDen})`;
            const replacement = `${numPart}/${denPart}`;
            str = str.substring(0, fracIndex) + replacement + str.substring(denEnd + 1);
            changed = true;
          }
        }
      }
    }
    
    // Traiter les exposants avec accolades
    pos = 0;
    while ((pos = str.indexOf('^{', pos)) !== -1) {
      const braceStart = pos + 1;
      const braceEnd = findMatchingBrace(str, braceStart);
      if (braceEnd !== -1) {
        const content = str.substring(braceStart + 1, braceEnd);
        const processed = processNested(content, depth + 1);
        str = str.substring(0, pos) + `^(${processed})` + str.substring(braceEnd + 1);
        pos += `^(${processed})`.length;
      } else {
        pos++;
      }
    }
    // Traiter les exposants simples
    str = str.replace(/\^(\d+)/g, '^$1');
    
    // Traiter les indices avec accolades
    pos = 0;
    while ((pos = str.indexOf('_{', pos)) !== -1) {
      const braceStart = pos + 1;
      const braceEnd = findMatchingBrace(str, braceStart);
      if (braceEnd !== -1) {
        const content = str.substring(braceStart + 1, braceEnd);
        const processed = processNested(content, depth + 1);
        str = str.substring(0, pos) + `_(${processed})` + str.substring(braceEnd + 1);
        pos += `_(${processed})`.length;
      } else {
        pos++;
      }
    }
    // Traiter les indices simples
    str = str.replace(/_(\d+)/g, '_$1');
    
    return str;
  };
  
  // Traiter les expressions imbriquées
  text = processNested(text);
  
  // Remplacer les autres commandes LaTeX (AVANT de retirer les backslashes)
  text = text
    .replace(/\\cdot/g, '*')
    .replace(/\\times/g, 'x')
    .replace(/\\div/g, '/')
    .replace(/\\pm/g, '+/-')
    .replace(/\\approx/g, '≈')
    .replace(/\\leq/g, '<=')
    .replace(/\\geq/g, '>=')
    .replace(/\\neq/g, '!=')
    .replace(/\\pi/g, 'pi')
    .replace(/\\infty/g, 'inf')
    .replace(/\\left\(/g, '(')
    .replace(/\\right\)/g, ')')
    .replace(/\\left\[/g, '[')
    .replace(/\\right\]/g, ']');
  
  // Retirer les accolades et backslashes restants (APRÈS avoir traité toutes les commandes)
  text = text
    .replace(/\{/g, '') // Retirer les accolades restantes
    .replace(/\}/g, '') // Retirer les accolades restantes
    .replace(/\\/g, '') // Retirer les backslashes restants
    .replace(/\s+/g, ' '); // Normaliser les espaces
  
  // Remplacer le caractère √ par "sqrt" pour une meilleure compatibilité (au cas où)
  text = text.replace(/√/g, 'sqrt');
  
  return text.trim();
};

/**
 * Génère un PDF avec le problème, les étapes et la solution (identique à la page de résultats)
 * @param {Object} data - Données à inclure dans le PDF
 * @param {string} data.problem - Le problème mathématique
 * @param {string} data.latex - LaTeX du problème
 * @param {string} data.solution - La solution
 * @param {Array} data.steps - Les étapes de résolution
 * @param {string} data.extractedLaTeX - LaTeX extrait (optionnel)
 */
export const generatePDFSimple = async (data) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  let yPosition = margin;
  const lineHeight = 7;
  const spacing = 5;

  const addText = (text, fontSize = 12, isBold = false, color = [0, 0, 0]) => {
    doc.setFontSize(fontSize);
    doc.setFont('helvetica', isBold ? 'bold' : 'normal');
    doc.setTextColor(color[0], color[1], color[2]);
    
    const lines = doc.splitTextToSize(text, pageWidth - 2 * margin);
    lines.forEach((line) => {
      if (yPosition > doc.internal.pageSize.getHeight() - margin - 10) {
        doc.addPage();
        yPosition = margin;
      }
      doc.text(line, margin, yPosition);
      yPosition += lineHeight;
    });
  };

  /**
   * Convertit une formule LaTeX en image et l'ajoute au PDF
   */
  const addFormulaAsImage = async (latex, fontSize = 12) => {
    try {
      // Créer un élément DOM temporaire
      const tempDiv = document.createElement('div');
      tempDiv.style.position = 'absolute';
      tempDiv.style.left = '-9999px';
      tempDiv.style.top = '0';
      tempDiv.style.padding = '15px';
      tempDiv.style.backgroundColor = '#ffffff';
      tempDiv.style.fontSize = `${fontSize}px`;
      tempDiv.style.display = 'inline-block';
      document.body.appendChild(tempDiv);
      
      // Rendre le LaTeX avec KaTeX
      katex.render(latex, tempDiv, {
        throwOnError: false,
        displayMode: true,
        output: 'html',
      });
      
      // Attendre un peu pour que le rendu soit complet
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Capturer l'élément en image
      const canvas = await html2canvas(tempDiv, {
        backgroundColor: '#ffffff',
        scale: 2, // Meilleure qualité
        logging: false,
        useCORS: true,
      });
      
      // Nettoyer
      document.body.removeChild(tempDiv);
      
      // Convertir en image et l'ajouter au PDF
      const imgData = canvas.toDataURL('image/png');
      const maxWidth = pageWidth - 2 * margin;
      const imgWidth = Math.min(canvas.width / 2, maxWidth); // Diviser par 2 car scale=2
      const imgHeight = (canvas.height / 2 * imgWidth) / (canvas.width / 2);
      
      if (yPosition + imgHeight > doc.internal.pageSize.getHeight() - margin - 10) {
        doc.addPage();
        yPosition = margin;
      }
      
      doc.addImage(imgData, 'PNG', margin, yPosition, imgWidth, imgHeight);
      yPosition += imgHeight + spacing;
      
      return true;
    } catch (error) {
      console.error('Erreur lors du rendu LaTeX en image:', error);
      // Fallback: utiliser le texte
      const readableText = latexToReadableText(latex);
      addText(readableText, fontSize);
      return false;
    }
  };
  
  const addFormula = (latex, fontSize = 12, color = [0, 0, 0]) => {
    // Convertir le LaTeX en texte lisible (fallback)
    const readableText = latexToReadableText(latex);
    doc.setFontSize(fontSize);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(color[0], color[1], color[2]);
    
    const lines = doc.splitTextToSize(readableText, pageWidth - 2 * margin);
    lines.forEach((line) => {
      if (yPosition > doc.internal.pageSize.getHeight() - margin - 10) {
        doc.addPage();
        yPosition = margin;
      }
      doc.text(line, margin, yPosition);
      yPosition += lineHeight;
    });
  };

  // Titre principal
  addText('Demarche de Solution', 18, true, [0, 168, 255]);
  yPosition += spacing * 2;

  // Section: Equation Détectée
  addText('Equation Détectée', 14, true);
  yPosition += lineHeight;
  const equation = data.latex || data.extractedLaTeX || data.problem || 'Non spécifié';
  // Essayer d'utiliser le rendu image, sinon fallback sur texte
  if (equation.includes('\\') || equation.includes('frac') || equation.includes('sqrt')) {
    await addFormulaAsImage(equation, 12);
  } else {
    addText(equation, 12);
  }
  
  // Afficher la solution si disponible (comme dans la page)
  if (data.solution) {
    yPosition += spacing;
    addText(`Solution: ${data.solution}`, 11, false, [100, 100, 100]);
  }
  
  yPosition += spacing * 2;

  // Section: Demarche de Solution
  addText('Demarche de Solution', 14, true);
  yPosition += lineHeight + spacing;

  // Étapes
  if (data.steps && data.steps.length > 0) {
    for (let index = 0; index < data.steps.length; index++) {
      const step = data.steps[index];
      
      // Numéro et titre de l'étape
      addText(`${index + 1}. ${step.title || `Étape ${index + 1}`}`, 12, true);
      yPosition += lineHeight;
      
      // Description
      if (step.description) {
        addText(step.description, 11);
        yPosition += lineHeight;
      }
      
      // Formule
      if (step.formula) {
        // Essayer d'utiliser le rendu image, sinon fallback sur texte
        if (step.formula.includes('\\') || step.formula.includes('frac') || step.formula.includes('sqrt')) {
          addText('Formule: ', 11, false, [0, 100, 200]);
          yPosition -= lineHeight; // Ajuster car addText a déjà incrémenté
          await addFormulaAsImage(step.formula, 11);
        } else {
          const formulaText = latexToReadableText(step.formula);
          addText(`Formule: ${formulaText}`, 11, false, [0, 100, 200]);
        }
      }
      
      // Explication
      if (step.explanation) {
        addText(step.explanation, 10, false, [80, 80, 80]);
        yPosition += lineHeight;
      }
      
      yPosition += spacing;
    }
  } else {
    // Si pas d'étapes, afficher la solution simple
    addText('1. Solution', 12, true);
    yPosition += lineHeight;
    addText(data.solution || 'Solution générée avec succès.', 11);
    yPosition += spacing;
  }

  // Section: Résultat Final
  const originalEquation = data.latex || data.extractedLaTeX || data.problem || '';
  const finalResult = calculateFinalResult(data, originalEquation);
  
  if (finalResult) {
    yPosition += spacing * 2;
    addText('Résultat Final', 14, true, [0, 168, 255]);
    yPosition += lineHeight;
    // Vérifier si c'est du LaTeX ou du texte simple
    if (finalResult.includes('\\') || finalResult.includes('frac') || finalResult.includes('sqrt')) {
      await addFormulaAsImage(finalResult, 12);
    } else {
      addText(finalResult, 12, false, [0, 168, 255]);
    }
  }

  const fileName = `solution_math_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
};

