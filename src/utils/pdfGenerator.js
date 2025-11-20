import jsPDF from 'jspdf';

/**
 * Génère un PDF avec le problème, les étapes et la solution
 * @param {Object} data - Données à inclure dans le PDF
 * @param {string} data.problem - Le problème mathématique
 * @param {string} data.latex - LaTeX du problème
 * @param {string} data.solution - La solution
 * @param {Array} data.steps - Les étapes de résolution
 */
export const generatePDFSimple = (data) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  let yPosition = margin;
  const lineHeight = 7;

  const addText = (text, fontSize = 12, isBold = false, color = [0, 0, 0]) => {
    doc.setFontSize(fontSize);
    doc.setFont('helvetica', isBold ? 'bold' : 'normal');
    doc.setTextColor(color[0], color[1], color[2]);
    
    const lines = doc.splitTextToSize(text, pageWidth - 2 * margin);
    lines.forEach((line) => {
      if (yPosition > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        yPosition = margin;
      }
      doc.text(line, margin, yPosition);
      yPosition += lineHeight;
    });
  };

  // Titre
  addText('Solution Mathématique', 20, true, [0, 168, 255]);
  yPosition += 10;

  // Problème
  addText('Problème Original:', 14, true);
  yPosition += lineHeight;
  addText(data.latex || data.problem || 'Non spécifié', 12);
  yPosition += 10;

  // Étapes
  if (data.steps && data.steps.length > 0) {
    addText('Étapes de Résolution:', 14, true);
    yPosition += lineHeight;
    
    data.steps.forEach((step, index) => {
      addText(`Étape ${index + 1}: ${step.title || ''}`, 12, true);
      yPosition += lineHeight;
      if (step.description) {
        addText(step.description, 11);
        yPosition += lineHeight;
      }
      if (step.formula) {
        addText(`Formule: ${step.formula}`, 11);
        yPosition += lineHeight;
      }
      yPosition += 5;
    });
  }

  // Solution
  yPosition += 10;
  addText('Solution Finale:', 14, true, [0, 168, 255]);
  yPosition += lineHeight;
  addText(data.solution || 'Non disponible', 12, false, [0, 168, 255]);

  const fileName = `solution_math_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
};

