/**
 * ============================================================================
 * VIVACRAFT: STUDENT STUDY COMPANION
 * Client-Side Application & Workflow Controller
 * Team: Komal, Anushka, Kristina, Parth
 * ============================================================================
 */

(() => {
  'use strict';

  // --------------------------------------------------------------------------
  // STATE MANAGEMENT
  // --------------------------------------------------------------------------
  const state = {
    // Current Document
    documentName: 'Transformers Capstone Report',
    documentText: '',
    chunks: [],
    easyNotes: null,
    detectedTopics: [],
    allQuestions: [],
    
    // User Settings
    questionCountSetting: 5,
    difficultySetting: 'Mixed',
    selectedTopics: new Set(),
    
    // Filtered Question Set for Study
    filteredQuestions: [],
    
    // Practice Session State
    practiceQueue: [],
    practiceIndex: 0,
    practiceAnswers: {},      // question_id -> { answer, feedback, skipped }
    sessionStats: {
      answered: 0,
      skipped: 0,
      topicsWell: new Set(),
      topicsRevise: new Set()
    },

    // Persistent Saved for Revision (localStorage)
    savedQuestionIds: new Set(),

    // Recent Notes (localStorage)
    recentNotes: []
  };

  // --------------------------------------------------------------------------
  // DOM ELEMENT SELECTORS
  // --------------------------------------------------------------------------
  const DOM = {
    // Navigation
    navBtns: document.querySelectorAll('.nav-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    brandLink: document.getElementById('brandLink'),
    notesSectionsBadge: document.getElementById('notesSectionsBadge'),
    questionsCountBadge: document.getElementById('questionsCountBadge'),
    revisionCountBadge: document.getElementById('revisionCountBadge'),
    btnOpenAbout: document.getElementById('btnOpenAbout'),

    // Notes Tab Elements
    uploadDropzone: document.getElementById('uploadDropzone'),
    notesFileInput: document.getElementById('notesFileInput'),
    btnTogglePaste: document.getElementById('btnTogglePaste'),
    pasteDrawer: document.getElementById('pasteDrawer'),
    pasteTextInput: document.getElementById('pasteTextInput'),
    btnCancelPaste: document.getElementById('btnCancelPaste'),
    btnSubmitPaste: document.getElementById('btnSubmitPaste'),
    sampleChips: document.querySelectorAll('.sample-chip'),
    recentNotesContainer: document.getElementById('recentNotesContainer'),
    recentNotesChips: document.getElementById('recentNotesChips'),
    threeStepsCard: document.getElementById('threeStepsCard'),

    // Document Preview & The 3 Options
    docPreviewCard: document.getElementById('docPreviewCard'),
    docPreviewName: document.getElementById('docPreviewName'),
    docPreviewStats: document.getElementById('docPreviewStats'),
    docSnippetText: document.getElementById('docSnippetText'),
    btnChangeDoc: document.getElementById('btnChangeDoc'),
    btnMakeEasyNotes: document.getElementById('btnMakeEasyNotes'),
    btnMakeVivaQuestions: document.getElementById('btnMakeVivaQuestions'),
    btnMakeBoth: document.getElementById('btnMakeBoth'),

    // Question Settings
    countSelector: document.getElementById('countSelector'),
    levelSelector: document.getElementById('levelSelector'),
    detectedTopicsList: document.getElementById('detectedTopicsList'),

    // Friendly Loader
    friendlyLoader: document.getElementById('friendlyLoader'),
    loaderStageText: document.getElementById('loaderStageText'),

    // Easy Notes Tab Elements
    notesDocBadge: document.getElementById('notesDocBadge'),
    notesDocHeading: document.getElementById('notesDocHeading'),
    notesDocSubtext: document.getElementById('notesDocSubtext'),
    btnDownloadNotesPdf: document.getElementById('btnDownloadNotesPdf'),
    btnGoToQuestionsFromNotes: document.getElementById('btnGoToQuestionsFromNotes'),
    btnStartPracticeFromNotes: document.getElementById('btnStartPracticeFromNotes'),
    notesTocNav: document.getElementById('notesTocNav'),
    notesContentContainer: document.getElementById('notesContentContainer'),

    // Questions Tab Elements
    questionsSetSubtext: document.getElementById('questionsSetSubtext'),
    btnStartPracticeFromSet: document.getElementById('btnStartPracticeFromSet'),
    btnDownloadMenu: document.getElementById('btnDownloadMenu'),
    downloadDropdown: document.getElementById('downloadDropdown'),
    inputSearchQuestions: document.getElementById('inputSearchQuestions'),
    filterTopicSelect: document.getElementById('filterTopicSelect'),
    filterLevelSelect: document.getElementById('filterLevelSelect'),
    questionsListContainer: document.getElementById('questionsListContainer'),

    // Practice Tab Elements
    practiceCounter: document.getElementById('practiceCounter'),
    practiceProgressFill: document.getElementById('practiceProgressFill'),
    practiceTopicBadge: document.getElementById('practiceTopicBadge'),
    practiceLevelBadge: document.getElementById('practiceLevelBadge'),
    practiceQuestionPrompt: document.getElementById('practiceQuestionPrompt'),
    btnTogglePracticeHint: document.getElementById('btnTogglePracticeHint'),
    practiceHintDrawer: document.getElementById('practiceHintDrawer'),
    tipArrow: document.getElementById('tipArrow'),
    practiceTipIntuition: document.getElementById('practiceTipIntuition'),
    practiceExpectedPointsList: document.getElementById('practiceExpectedPointsList'),
    practiceAnswerInput: document.getElementById('practiceAnswerInput'),
    practiceWordCount: document.getElementById('practiceWordCount'),
    btnPracticeDictate: document.getElementById('btnPracticeDictate'),
    dictateStatusText: document.getElementById('dictateStatusText'),
    btnSkipPractice: document.getElementById('btnSkipPractice'),
    btnFinishPracticeEarly: document.getElementById('btnFinishPracticeEarly'),
    btnCheckAnswer: document.getElementById('btnCheckAnswer'),

    // Practice Feedback Card
    practiceFeedbackCard: document.getElementById('practiceFeedbackCard'),
    verdictIcon: document.getElementById('verdictIcon'),
    verdictHeadline: document.getElementById('verdictHeadline'),
    verdictSubtext: document.getElementById('verdictSubtext'),
    feedbackCoveredList: document.getElementById('feedbackCoveredList'),
    feedbackMissingList: document.getElementById('feedbackMissingList'),
    feedbackSuggestedAnswer: document.getElementById('feedbackSuggestedAnswer'),
    btnFeedbackFindInNotes: document.getElementById('btnFeedbackFindInNotes'),
    btnNextPracticeQuestion: document.getElementById('btnNextPracticeQuestion'),

    // Progress Tab Elements
    statAnswered: document.getElementById('statAnswered'),
    statSkipped: document.getElementById('statSkipped'),
    statCoveredCount: document.getElementById('statCoveredCount'),
    statReviseCount: document.getElementById('statReviseCount'),
    topicsWellList: document.getElementById('topicsWellList'),
    topicsToReviseList: document.getElementById('topicsToReviseList'),
    btnProgressRevise: document.getElementById('btnProgressRevise'),
    btnProgressTryAgain: document.getElementById('btnProgressTryAgain'),
    btnProgressReviewAnswers: document.getElementById('btnProgressReviewAnswers'),
    savedRevisionCount: document.getElementById('savedRevisionCount'),
    savedRevisionList: document.getElementById('savedRevisionList'),
    emptySavedNote: document.getElementById('emptySavedNote'),
    btnPracticeSaved: document.getElementById('btnPracticeSaved'),

    // Modals & Toast
    notesCitationModal: document.getElementById('notesCitationModal'),
    modalCitationTitle: document.getElementById('modalCitationTitle'),
    modalCitationQuote: document.getElementById('modalCitationQuote'),
    modalCitationContext: document.getElementById('modalCitationContext'),
    btnCloseCitationModal: document.getElementById('btnCloseCitationModal'),
    btnDismissCitation: document.getElementById('btnDismissCitation'),

    aboutModal: document.getElementById('aboutModal'),
    btnCloseAboutModal: document.getElementById('btnCloseAboutModal'),
    btnDismissAbout: document.getElementById('btnDismissAbout'),
    appToast: document.getElementById('appToast'),
    toastMessage: document.getElementById('toastMessage')
  };

  // --------------------------------------------------------------------------
  // INITIALIZATION
  // --------------------------------------------------------------------------
  async function init() {
    loadPersistentData();
    bindEvents();
    setupSpeechRecognition();

    try {
      showLoader('Reading your notes…');
      const res = await fetch('/api/state');
      if (res.ok) {
        const data = await res.json();
        populateDocumentData(data);
      }
    } catch (err) {
      console.warn('Initial state fetch error:', err);
    } finally {
      hideLoader();
    }
  }

  // --------------------------------------------------------------------------
  // LOCAL STORAGE PERSISTENCE
  // --------------------------------------------------------------------------
  function loadPersistentData() {
    try {
      const saved = JSON.parse(localStorage.getItem('vivacraft_saved_questions') || '[]');
      state.savedQuestionIds = new Set(saved);
      updateRevisionBadge();
    } catch {
      state.savedQuestionIds = new Set();
    }

    try {
      state.recentNotes = JSON.parse(localStorage.getItem('vivacraft_recent_notes') || '[]');
      renderRecentNotes();
    } catch {
      state.recentNotes = [];
    }
  }

  function saveRecentNote(name) {
    if (!name) return;
    state.recentNotes = [name, ...state.recentNotes.filter(n => n !== name)].slice(0, 4);
    try {
      localStorage.setItem('vivacraft_recent_notes', JSON.stringify(state.recentNotes));
    } catch {}
    renderRecentNotes();
  }

  function toggleSaveQuestion(questionId) {
    if (state.savedQuestionIds.has(questionId)) {
      state.savedQuestionIds.delete(questionId);
      showToast('Removed from revision');
    } else {
      state.savedQuestionIds.add(questionId);
      showToast('Saved for revision');
    }

    try {
      localStorage.setItem(
        'vivacraft_saved_questions',
        JSON.stringify(Array.from(state.savedQuestionIds))
      );
    } catch {}

    updateRevisionBadge();
    renderQuestionsList();
    renderSavedRevisionList();
  }

  function updateRevisionBadge() {
    const count = state.savedQuestionIds.size;
    DOM.revisionCountBadge.textContent = count;
    DOM.savedRevisionCount.textContent = count;
    DOM.revisionCountBadge.classList.toggle('hidden', count === 0);
    DOM.btnPracticeSaved.disabled = (count === 0);
  }

  // --------------------------------------------------------------------------
  // TAB NAVIGATION
  // --------------------------------------------------------------------------
  function switchTab(tabId) {
    DOM.navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    DOM.tabPanes.forEach(pane => {
      pane.classList.toggle('active', pane.id === tabId);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (tabId === 'tab-easynotes') {
      renderEasyNotesTab();
    } else if (tabId === 'tab-questions') {
      renderQuestionsList();
    } else if (tabId === 'tab-practice') {
      if (state.practiceQueue.length === 0) {
        startPracticeSession();
      }
    } else if (tabId === 'tab-progress') {
      renderProgressTab();
    }
  }

  // --------------------------------------------------------------------------
  // DOCUMENT INGESTION & DATA POPULATION
  // --------------------------------------------------------------------------
  function populateDocumentData(data) {
    state.documentName = data.document_name || 'Your Notes';
    state.documentText = data.document_text || '';
    state.chunks = data.chunks || [];
    state.allQuestions = data.questions || [];
    state.easyNotes = data.easy_notes || null;

    // Extract unique detected topics
    const topicsSet = new Set();
    state.allQuestions.forEach(q => {
      if (q.section_title) topicsSet.add(q.section_title);
    });
    (data.textrank_keyphrases || []).forEach(kp => {
      if (kp.keyphrase && kp.keyphrase.length > 3) {
        topicsSet.add(capitalizeWords(kp.keyphrase));
      }
    });

    state.detectedTopics = Array.from(topicsSet).slice(0, 10);
    state.selectedTopics = new Set(state.detectedTopics);

    // Update UI elements on Notes tab
    DOM.docPreviewName.textContent = state.documentName;
    const wordCount = (data.stats && data.stats.total_words) || state.documentText.split(/\s+/).length || 0;
    const sectionCount = state.chunks.length || 1;
    DOM.docPreviewStats.textContent = `${wordCount} words • ${sectionCount} sections`;

    // Preview snippet
    const snippet = state.documentText.replace(/\s+/g, ' ').slice(0, 260) || 'Your notes are ready.';
    DOM.docSnippetText.textContent = `"${snippet}..."`;

    renderTopicChips();
    populateTopicFilters();

    // Badges in header
    const numSections = (state.easyNotes && state.easyNotes.sections) ? state.easyNotes.sections.length : sectionCount;
    DOM.notesSectionsBadge.textContent = numSections;
    DOM.notesSectionsBadge.classList.toggle('hidden', numSections === 0);

    DOM.questionsCountBadge.textContent = state.allQuestions.length;
    DOM.questionsCountBadge.classList.toggle('hidden', state.allQuestions.length === 0);

    // Update Easy Notes tab headers
    DOM.notesDocHeading.textContent = `Easy Notes: ${state.documentName}`;
    DOM.notesDocSubtext.textContent = `${numSections} sections organized with key definitions, formulas, and page references.`;

    saveRecentNote(state.documentName);
  }

  function renderTopicChips() {
    DOM.detectedTopicsList.innerHTML = '';
    state.detectedTopics.forEach(topic => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = `topic-chip ${state.selectedTopics.has(topic) ? 'selected' : ''}`;
      chip.textContent = topic;
      chip.addEventListener('click', () => {
        if (state.selectedTopics.has(topic)) {
          state.selectedTopics.delete(topic);
          chip.classList.remove('selected');
        } else {
          state.selectedTopics.add(topic);
          chip.classList.add('selected');
        }
      });
      DOM.detectedTopicsList.appendChild(chip);
    });
  }

  function renderRecentNotes() {
    if (!state.recentNotes.length) {
      DOM.recentNotesContainer.classList.add('hidden');
      return;
    }
    DOM.recentNotesChips.innerHTML = '';
    state.recentNotes.forEach(name => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'recent-chip';
      chip.textContent = name;
      chip.addEventListener('click', () => {
        if (name.includes('Transformer')) {
          loadSampleDocument('transformers_and_attention.txt');
        } else if (name.includes('Raft')) {
          loadSampleDocument('distributed_systems_raft.txt');
        }
      });
      DOM.recentNotesChips.appendChild(chip);
    });
    DOM.recentNotesContainer.classList.remove('hidden');
  }

  // --------------------------------------------------------------------------
  // THE 3 CORE OPTIONS ACTIONS
  // --------------------------------------------------------------------------
  async function handleMakeEasyNotes() {
    showLoader('Organizing notes by topics and headings…');
    try {
      const res = await fetch('/api/notes?regenerate=true');
      if (res.ok) {
        state.easyNotes = await res.json();
      }
    } catch (err) {
      console.warn('Failed to refresh easy notes:', err);
    }
    setTimeout(() => {
      hideLoader();
      switchTab('tab-easynotes');
      showToast('Easy Notes ready to study');
    }, 450);
  }

  function handleMakeVivaQuestions() {
    showLoader('Preparing your questions…');
    setTimeout(() => {
      createQuestionsFromSettings();
    }, 400);
  }

  async function handleMakeBoth() {
    showLoader('Creating easy notes and viva questions…');
    try {
      const res = await fetch('/api/notes?regenerate=true');
      if (res.ok) {
        state.easyNotes = await res.json();
      }
    } catch (err) {
      console.warn('Failed to refresh easy notes:', err);
    }
    setTimeout(() => {
      createQuestionsFromSettings(false); // Prepare questions in background
      hideLoader();
      switchTab('tab-easynotes');
      showToast('Easy notes and viva questions ready!');
    }, 500);
  }

  function createQuestionsFromSettings(switchImmediately = true) {
    let pool = [...state.allQuestions];

    if (state.selectedTopics.size > 0) {
      pool = pool.filter(q => {
        return state.selectedTopics.has(q.section_title) ||
               state.selectedTopics.has(q.target_concept) ||
               Array.from(state.selectedTopics).some(t => 
                 (q.question_text || '').toLowerCase().includes(t.toLowerCase())
               );
      });
    }

    if (state.difficultySetting !== 'Mixed') {
      const levelFiltered = pool.filter(q => q.difficulty === state.difficultySetting);
      if (levelFiltered.length >= 3) {
        pool = levelFiltered;
      }
    }

    if (pool.length < 3) {
      pool = [...state.allQuestions];
    }

    state.filteredQuestions = pool.slice(0, state.questionCountSetting);

    if (switchImmediately) {
      hideLoader();
      switchTab('tab-questions');
      showToast(`${state.filteredQuestions.length} viva questions ready`);
    }
  }

  // --------------------------------------------------------------------------
  // EASY NOTES TAB (STRUCTURED STUDY INTERFACE)
  // --------------------------------------------------------------------------
  function renderEasyNotesTab() {
    const notesData = state.easyNotes;
    if (!notesData || !notesData.sections || !notesData.sections.length) {
      DOM.notesContentContainer.innerHTML = `
        <div class="card" style="padding: 2.5rem; text-align: center; color: var(--text-muted);">
          <p>Easy Notes are being compiled from your study material...</p>
        </div>
      `;
      return;
    }

    // Render Sidebar Table of Contents
    DOM.notesTocNav.innerHTML = '';
    notesData.sections.forEach((sec, idx) => {
      const link = document.createElement('a');
      link.className = `toc-link ${idx === 0 ? 'active' : ''}`;
      link.href = `#note_sec_${idx}`;
      link.innerHTML = `<span>${idx + 1}.</span> <span>${escapeHTML(sec.heading)}</span>`;
      link.addEventListener('click', (e) => {
        e.preventDefault();
        DOM.notesTocNav.querySelectorAll('.toc-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        const target = document.getElementById(`note_sec_${idx}`);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
      DOM.notesTocNav.appendChild(link);
    });

    // Render Section Note Cards
    DOM.notesContentContainer.innerHTML = '';
    notesData.sections.forEach((sec, idx) => {
      const card = document.createElement('article');
      card.className = 'section-note-card';
      card.id = `note_sec_${idx}`;

      if (sec.is_unreadable) {
        card.innerHTML = `
          <div class="note-card-header">
            <h3 class="note-heading">${escapeHTML(sec.heading)}</h3>
            <span class="page-ref-badge">${escapeHTML(sec.page_ref)}</span>
          </div>
          <div class="unreadable-warning-card">
            <strong>Note:</strong> This page could not be read clearly (scanned image or insufficient text). Try providing selectable text.
          </div>
        `;
        DOM.notesContentContainer.appendChild(card);
        return;
      }

      // 1. What is [Topic]? Introductory explanation
      const whatIsText = sec.what_is || sec.summary || '';
      const whatIsHTML = whatIsText ? `
        <div class="note-summary-box">
          <span class="note-summary-label">What is ${escapeHTML(sec.heading)}?</span>
          <p class="note-summary-text">${escapeHTML(whatIsText)}</p>
        </div>
      ` : '';

      // 2. Important Points (with bold category labels)
      let pointsHTML = '';
      const pointsList = sec.key_points || (sec.definitions ? sec.definitions.map(d => ({ label: d.term, text: d.explanation })) : []);
      if (pointsList && pointsList.length) {
        pointsHTML = `
          <div class="note-block">
            <h4 class="note-block-title">Important Points</h4>
            <div class="definitions-list">
              ${pointsList.map(pt => `
                <div class="definition-item">
                  <span class="def-term">${escapeHTML(pt.label)}:</span>
                  <span class="def-meaning">${escapeHTML(pt.text)}</span>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }

      // 3. How It Works (Step-by-Step) - only when genuine steps exist
      let stepsHTML = '';
      if (sec.working_steps && sec.working_steps.length) {
        stepsHTML = `
          <div class="note-block">
            <h4 class="note-block-title">How It Works (Step-by-Step)</h4>
            <ol class="note-bullet-list">
              ${sec.working_steps.map(step => `<li>${escapeHTML(step)}</li>`).join('')}
            </ol>
          </div>
        `;
      }

      // 4. Formulas & Equations (with variable breakdowns)
      let formulasHTML = '';
      if (sec.formulas && sec.formulas.length) {
        formulasHTML = `
          <div class="note-block">
            <h4 class="note-block-title">Key Formulas & Equations</h4>
            ${sec.formulas.map(f => {
              if (typeof f === 'object' && f !== null) {
                return `
                  <div class="formula-box">
                    <div>${escapeHTML(f.expression || '')}</div>
                    ${f.variables ? `<div style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted); margin-top: 0.25rem;">${escapeHTML(f.variables)}</div>` : ''}
                  </div>
                `;
              }
              return `<div class="formula-box">${escapeHTML(f)}</div>`;
            }).join('')}
          </div>
        `;
      }

      // 5. Comparisons & Trade-offs
      let comparisonsHTML = '';
      if (sec.comparisons && sec.comparisons.length) {
        comparisonsHTML = `
          <div class="note-block">
            <h4 class="note-block-title">Comparisons & Trade-offs</h4>
            <div class="comparisons-card">
              ${sec.comparisons.map(c => {
                if (typeof c === 'object' && c !== null) {
                  return `
                    <div style="margin-bottom: 0.5rem;">
                      <strong>${escapeHTML(c.compared || 'Comparison')}:</strong>
                      <p style="margin: 0.2rem 0 0 0;">${escapeHTML(c.details || '')}</p>
                    </div>
                  `;
                }
                return `<p style="margin-bottom: 0.35rem;">&bull; ${escapeHTML(c)}</p>`;
              }).join('')}
            </div>
          </div>
        `;
      }

      // 6. Viva Focus Tip (Never cut off)
      let tipHTML = '';
      const tipText = sec.viva_focus || sec.key_takeaway || '';
      if (tipText) {
        tipHTML = `
          <div class="viva-tip-card">
            <strong>${escapeHTML(tipText)}</strong>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="note-card-header">
          <div>
            <h3 class="note-heading">${escapeHTML(sec.heading)}</h3>
          </div>
          <span class="page-ref-badge">${escapeHTML(sec.page_ref)}</span>
        </div>

        ${whatIsHTML}
        ${pointsHTML}
        ${stepsHTML}
        ${formulasHTML}
        ${comparisonsHTML}
        ${tipHTML}
      `;

      DOM.notesContentContainer.appendChild(card);
    });
  }

  // --------------------------------------------------------------------------
  // VIVA QUESTIONS TAB (STUDY QUESTION SET)
  // --------------------------------------------------------------------------
  function populateTopicFilters() {
    DOM.filterTopicSelect.innerHTML = '<option value="all">All topics</option>';
    const topics = new Set();
    state.allQuestions.forEach(q => {
      if (q.section_title) topics.add(q.section_title);
    });
    topics.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      DOM.filterTopicSelect.appendChild(opt);
    });
  }

  function renderQuestionsList() {
    const searchTerm = (DOM.inputSearchQuestions.value || '').toLowerCase().trim();
    const topicFilter = DOM.filterTopicSelect.value;
    const levelFilter = DOM.filterLevelSelect.value;

    const baseList = state.filteredQuestions.length ? state.filteredQuestions : state.allQuestions;

    const visibleQuestions = baseList.filter(q => {
      const matchesSearch = !searchTerm ||
        (q.question_text || '').toLowerCase().includes(searchTerm) ||
        (q.section_title || '').toLowerCase().includes(searchTerm) ||
        (q.target_concept || '').toLowerCase().includes(searchTerm);

      const matchesTopic = (topicFilter === 'all') || (q.section_title === topicFilter);
      const matchesLevel = (levelFilter === 'all') || (q.difficulty === levelFilter);

      return matchesSearch && matchesTopic && matchesLevel;
    });

    DOM.questionsSetSubtext.textContent = `${visibleQuestions.length} questions from ${state.documentName}`;

    if (!visibleQuestions.length) {
      DOM.questionsListContainer.innerHTML = `
        <div class="card" style="padding: 2.5rem; text-align: center; color: var(--text-muted);">
          <p>No questions match your current search or topic filter.</p>
          <button class="btn btn-sm btn-secondary" style="margin-top: 0.75rem;" id="btnResetFilters">Reset filters</button>
        </div>
      `;
      document.getElementById('btnResetFilters')?.addEventListener('click', () => {
        DOM.inputSearchQuestions.value = '';
        DOM.filterTopicSelect.value = 'all';
        DOM.filterLevelSelect.value = 'all';
        renderQuestionsList();
      });
      return;
    }

    DOM.questionsListContainer.innerHTML = '';
    visibleQuestions.forEach((q, idx) => {
      const isSaved = state.savedQuestionIds.has(q.question_id);
      const levelClass = (q.difficulty === 'Easy') ? 'level-easy' : 
                         (q.difficulty === 'Challenging') ? 'level-challenging' : 'level-medium';

      const card = document.createElement('div');
      card.className = 'question-item-card';
      card.dataset.id = q.question_id;

      card.innerHTML = `
        <div class="question-card-top">
          <div class="question-num-badges">
            <span class="q-number-pill">Question ${idx + 1}</span>
            <span class="q-topic-tag">${escapeHTML(q.section_title || 'Core Topic')}</span>
            <span class="q-level-tag ${levelClass}">${escapeHTML(q.difficulty || 'Medium')}</span>
          </div>
          <button class="btn-bookmark ${isSaved ? 'saved' : ''}" data-id="${q.question_id}" title="Save for revision">
            <span>${isSaved ? 'Saved' : 'Save for revision'}</span>
          </button>
        </div>

        <p class="q-prompt-text">${escapeHTML(q.question_text)}</p>

        <div class="q-card-actions">
          <div class="q-action-left">
            <button class="btn btn-sm btn-secondary btn-show-answer" data-id="${q.question_id}">
              Show answer
            </button>
            <button class="btn-text btn-find-notes" data-id="${q.question_id}">
              Find it in my notes &rarr;
            </button>
          </div>
          <button class="btn btn-sm btn-outline btn-practise-this" data-id="${q.question_id}">
            Practise this &rarr;
          </button>
        </div>

        <div class="revealed-answer-box hidden" id="ansBox_${q.question_id}">
          <div class="revealed-answer-title">Suggested Answer</div>
          <p class="revealed-answer-text">${escapeHTML(q.suggested_answer || q.model_answer || 'Suggested answer available in practice.')}</p>
        </div>
      `;

      card.querySelector('.btn-bookmark').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleSaveQuestion(q.question_id);
      });

      card.querySelector('.btn-show-answer').addEventListener('click', (e) => {
        const box = card.querySelector(`#ansBox_${q.question_id}`);
        const isHidden = box.classList.contains('hidden');
        box.classList.toggle('hidden');
        e.target.textContent = isHidden ? 'Hide answer' : 'Show answer';
      });

      card.querySelector('.btn-find-notes').addEventListener('click', () => {
        openCitationModal(q);
      });

      card.querySelector('.btn-practise-this').addEventListener('click', () => {
        startPracticeWithQuestions([q]);
      });

      DOM.questionsListContainer.appendChild(card);
    });
  }

  // --------------------------------------------------------------------------
  // PRACTISE VIVA TAB (FOCUSED 1-BY-1 PRACTICE)
  // --------------------------------------------------------------------------
  function startPracticeSession() {
    const list = state.filteredQuestions.length ? state.filteredQuestions : state.allQuestions;
    startPracticeWithQuestions(list);
  }

  function startPracticeWithQuestions(questionsList) {
    if (!questionsList || !questionsList.length) {
      showToast('No questions available to practise.');
      return;
    }
    state.practiceQueue = [...questionsList];
    state.practiceIndex = 0;
    state.practiceAnswers = {};
    state.sessionStats = {
      answered: 0,
      skipped: 0,
      topicsWell: new Set(),
      topicsRevise: new Set()
    };

    switchTab('tab-practice');
    renderCurrentPracticeQuestion();
  }

  function renderCurrentPracticeQuestion() {
    if (state.practiceIndex >= state.practiceQueue.length) {
      finishPracticeSession();
      return;
    }

    const q = state.practiceQueue[state.practiceIndex];
    const total = state.practiceQueue.length;
    const currentNum = state.practiceIndex + 1;

    DOM.practiceFeedbackCard.classList.add('hidden');
    DOM.practiceAnswerInput.value = '';
    DOM.practiceWordCount.textContent = '0';
    DOM.practiceHintDrawer.classList.add('hidden');
    DOM.tipArrow.innerHTML = '&#9662;';

    DOM.practiceCounter.textContent = `Question ${currentNum} of ${total}`;
    const progressPct = Math.round((currentNum / total) * 100);
    DOM.practiceProgressFill.style.width = `${progressPct}%`;

    DOM.practiceTopicBadge.textContent = q.section_title || 'Core Topic';
    DOM.practiceLevelBadge.textContent = q.difficulty || 'Medium';
    DOM.practiceQuestionPrompt.textContent = q.question_text;

    if (q.study_tips) {
      DOM.practiceTipIntuition.textContent = q.study_tips.intuition || 'Start with a clear, direct summary in 1-2 sentences.';
    }
    DOM.practiceExpectedPointsList.innerHTML = '';
    (q.expected_points || ['Clear definition', 'Underlying mechanism', 'Practical reasoning']).forEach(pt => {
      const li = document.createElement('li');
      li.textContent = pt;
      DOM.practiceExpectedPointsList.appendChild(li);
    });

    DOM.practiceAnswerInput.focus();
  }

  async function checkStudentAnswer() {
    const currentQ = state.practiceQueue[state.practiceIndex];
    const studentAnswer = DOM.practiceAnswerInput.value.trim();

    if (!studentAnswer) {
      DOM.practiceAnswerInput.focus();
      showToast('Type or speak your answer first.');
      return;
    }

    DOM.btnCheckAnswer.disabled = true;
    DOM.btnCheckAnswer.innerHTML = '<span>Checking...</span>';

    try {
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: currentQ.question_id,
          student_answer: studentAnswer
        })
      });

      if (!res.ok) throw new Error('Evaluation failed');
      const evalData = await res.json();
      displayPracticeFeedback(currentQ, evalData, studentAnswer);
    } catch (err) {
      console.warn('Evaluation error:', err);
      displayPracticeFeedback(currentQ, {
        verdict_message: 'Good start — review your answer against the suggested notes.',
        key_points_covered: ['Main concept'],
        what_to_add: ['Details from your notes'],
        suggested_answer: currentQ.suggested_answer || currentQ.model_answer,
        source_citation: currentQ.source_citation,
        final_score: 70
      }, studentAnswer);
    } finally {
      DOM.btnCheckAnswer.disabled = false;
      DOM.btnCheckAnswer.innerHTML = '<span>Check my answer</span>';
    }
  }

  function displayPracticeFeedback(question, evalData, studentAnswer) {
    state.sessionStats.answered += 1;
    const score = evalData.final_score || 70;
    const topic = question.section_title || 'General';

    if (score >= 65) {
      state.sessionStats.topicsWell.add(topic);
    } else {
      state.sessionStats.topicsRevise.add(topic);
    }

    state.practiceAnswers[question.question_id] = {
      answer: studentAnswer,
      feedback: evalData,
      skipped: false
    };

    const verdict = evalData.verdict_message || 'You covered the main idea.';
    DOM.verdictHeadline.textContent = verdict;
    if (verdict.includes('main idea')) {
      DOM.verdictIcon.textContent = '';
      DOM.verdictSubtext.textContent = 'Well done! You articulated the core intuition clearly.';
    } else if (verdict.includes('Good start')) {
      DOM.verdictIcon.textContent = '';
      DOM.verdictSubtext.textContent = 'Good progress. Consider adding how the mechanism functions step-by-step.';
    } else {
      DOM.verdictIcon.textContent = '';
      DOM.verdictSubtext.textContent = 'Review this section in your notes and try answering again.';
    }

    // What you covered
    DOM.feedbackCoveredList.innerHTML = '';
    const covered = evalData.key_points_covered || evalData.covered_concepts || [];
    if (covered.length) {
      covered.slice(0, 4).forEach(pt => {
        const li = document.createElement('li');
        li.textContent = capitalizeWords(pt);
        DOM.feedbackCoveredList.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'Mentioned general context';
      DOM.feedbackCoveredList.appendChild(li);
    }

    // What to add
    DOM.feedbackMissingList.innerHTML = '';
    const missing = evalData.what_to_add || evalData.missing_concepts || [];
    if (missing.length) {
      missing.slice(0, 4).forEach(pt => {
        const li = document.createElement('li');
        li.textContent = capitalizeWords(pt);
        DOM.feedbackMissingList.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'Review specific technical parameters in the suggested answer';
      DOM.feedbackMissingList.appendChild(li);
    }

    // Suggested Answer
    DOM.feedbackSuggestedAnswer.textContent = evalData.suggested_answer || question.suggested_answer || question.model_answer || question.source_citation;

    DOM.btnFeedbackFindInNotes.onclick = () => openCitationModal(question);

    DOM.practiceFeedbackCard.classList.remove('hidden');
    DOM.practiceFeedbackCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function skipCurrentPracticeQuestion() {
    const q = state.practiceQueue[state.practiceIndex];
    state.sessionStats.skipped += 1;
    if (q.section_title) {
      state.sessionStats.topicsRevise.add(q.section_title);
    }
    state.practiceAnswers[q.question_id] = { skipped: true };

    state.practiceIndex += 1;
    renderCurrentPracticeQuestion();
  }

  function finishPracticeSession() {
    switchTab('tab-progress');
  }

  // --------------------------------------------------------------------------
  // MY PROGRESS TAB (RESULTS & REVISION)
  // --------------------------------------------------------------------------
  function renderProgressTab() {
    DOM.statAnswered.textContent = state.sessionStats.answered;
    DOM.statSkipped.textContent = state.sessionStats.skipped;
    DOM.statCoveredCount.textContent = state.sessionStats.topicsWell.size;
    DOM.statReviseCount.textContent = state.sessionStats.topicsRevise.size;

    DOM.topicsWellList.innerHTML = '';
    if (state.sessionStats.topicsWell.size) {
      state.sessionStats.topicsWell.forEach(topic => {
        const tag = document.createElement('span');
        tag.className = 'progress-topic-tag tag-good';
        tag.textContent = topic;
        DOM.topicsWellList.appendChild(tag);
      });
    } else {
      DOM.topicsWellList.innerHTML = '<span class="empty-state-text">Complete questions in practice to see topics covered well.</span>';
    }

    DOM.topicsToReviseList.innerHTML = '';
    if (state.sessionStats.topicsRevise.size) {
      state.sessionStats.topicsRevise.forEach(topic => {
        const tag = document.createElement('span');
        tag.className = 'progress-topic-tag tag-revise';
        tag.textContent = topic;
        DOM.topicsToReviseList.appendChild(tag);
      });
    } else {
      DOM.topicsToReviseList.innerHTML = '<span class="empty-state-text">No topics flagged for revision yet. Great job!</span>';
    }

    renderSavedRevisionList();
  }

  function renderSavedRevisionList() {
    const savedIds = Array.from(state.savedQuestionIds);
    DOM.savedRevisionCount.textContent = savedIds.length;
    DOM.emptySavedNote.classList.toggle('hidden', savedIds.length > 0);
    DOM.btnPracticeSaved.disabled = (savedIds.length === 0);

    const savedQuestions = state.allQuestions.filter(q => state.savedQuestionIds.has(q.question_id));
    DOM.savedRevisionList.innerHTML = '';

    savedQuestions.forEach(q => {
      const row = document.createElement('div');
      row.className = 'saved-q-row';
      row.innerHTML = `
        <div class="saved-q-info">
          <span class="saved-q-topic">${escapeHTML(q.section_title || 'Topic')}</span>
          <span class="saved-q-text">${escapeHTML(q.question_text)}</span>
        </div>
        <div class="saved-q-actions">
          <button class="btn btn-sm btn-outline btn-practise-one" data-id="${q.question_id}">Practise</button>
          <button class="btn-text btn-remove-saved" data-id="${q.question_id}" style="color: var(--text-light);">&times;</button>
        </div>
      `;

      row.querySelector('.btn-practise-one').addEventListener('click', () => {
        startPracticeWithQuestions([q]);
      });

      row.querySelector('.btn-remove-saved').addEventListener('click', () => {
        toggleSaveQuestion(q.question_id);
      });

      DOM.savedRevisionList.appendChild(row);
    });
  }

  // --------------------------------------------------------------------------
  // CITATION MODAL (FIND IT IN YOUR NOTES)
  // --------------------------------------------------------------------------
  function openCitationModal(question) {
    DOM.modalCitationTitle.textContent = `Section: ${question.section_title || 'Your Notes'}`;
    DOM.modalCitationQuote.textContent = `"${question.source_citation || 'Supporting sentence from your report.'}"`;

    let contextText = '';
    const chunk = state.chunks.find(c => c.chunk_id === question.source_chunk_id);
    if (chunk) {
      contextText = chunk.text;
    } else {
      contextText = state.documentText.slice(0, 400);
    }
    DOM.modalCitationContext.textContent = contextText;

    DOM.notesCitationModal.classList.remove('hidden');
  }

  function closeCitationModal() {
    DOM.notesCitationModal.classList.add('hidden');
  }

  // --------------------------------------------------------------------------
  // SPEECH RECOGNITION (WEB SPEECH API)
  // --------------------------------------------------------------------------
  let speechRecognizer = null;
  let isListening = false;

  function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      DOM.btnPracticeDictate.title = 'Voice dictation is not supported in this browser. You can type your answer.';
      return;
    }

    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = true;
    speechRecognizer.interimResults = true;
    speechRecognizer.lang = 'en-US';

    speechRecognizer.onstart = () => {
      isListening = true;
      DOM.btnPracticeDictate.classList.add('listening');
      DOM.dictateStatusText.textContent = 'Listening...';
    };

    speechRecognizer.onend = () => {
      isListening = false;
      DOM.btnPracticeDictate.classList.remove('listening');
      DOM.dictateStatusText.textContent = 'Speak answer';
    };

    speechRecognizer.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript + ' ';
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      if (final) {
        DOM.practiceAnswerInput.value = (DOM.practiceAnswerInput.value + ' ' + final).trim();
        updateWordCount();
      }
    };
  }

  function toggleSpeechDictation() {
    if (!speechRecognizer) {
      showToast('Voice dictation is not supported in this browser.');
      return;
    }
    if (isListening) {
      speechRecognizer.stop();
    } else {
      speechRecognizer.start();
    }
  }

  function updateWordCount() {
    const text = DOM.practiceAnswerInput.value.trim();
    const count = text ? text.split(/\s+/).length : 0;
    DOM.practiceWordCount.textContent = count;
  }

  // --------------------------------------------------------------------------
  // EVENT LISTENERS BINDING
  // --------------------------------------------------------------------------
  function bindEvents() {
    // Navigation Tabs
    DOM.navBtns.forEach(btn => {
      btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    DOM.brandLink.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('tab-notes');
    });

    // The 3 Options on My Notes
    DOM.btnMakeEasyNotes.addEventListener('click', handleMakeEasyNotes);
    DOM.btnMakeVivaQuestions.addEventListener('click', handleMakeVivaQuestions);
    DOM.btnMakeBoth.addEventListener('click', handleMakeBoth);

    // Easy Notes tab top actions
    DOM.btnGoToQuestionsFromNotes.addEventListener('click', () => {
      switchTab('tab-questions');
    });
    DOM.btnStartPracticeFromNotes.addEventListener('click', startPracticeSession);

    // About Modal
    DOM.btnOpenAbout.addEventListener('click', () => DOM.aboutModal.classList.remove('hidden'));
    DOM.btnCloseAboutModal.addEventListener('click', () => DOM.aboutModal.classList.add('hidden'));
    DOM.btnDismissAbout.addEventListener('click', () => DOM.aboutModal.classList.add('hidden'));

    // Citation Modal
    DOM.btnCloseCitationModal.addEventListener('click', closeCitationModal);
    DOM.btnDismissCitation.addEventListener('click', closeCitationModal);

    [DOM.notesCitationModal, DOM.aboutModal].forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
      });
    });

    // File Upload via Input
    DOM.notesFileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      await uploadFile(file);
    });

    // Drag and Drop
    DOM.uploadDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      DOM.uploadDropzone.classList.add('dragover');
    });
    DOM.uploadDropzone.addEventListener('dragleave', () => {
      DOM.uploadDropzone.classList.remove('dragover');
    });
    DOM.uploadDropzone.addEventListener('drop', async (e) => {
      e.preventDefault();
      DOM.uploadDropzone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file) await uploadFile(file);
    });

    // Paste Text Drawer Toggle
    DOM.btnTogglePaste.addEventListener('click', () => {
      DOM.pasteDrawer.classList.toggle('hidden');
      if (!DOM.pasteDrawer.classList.contains('hidden')) {
        DOM.pasteTextInput.focus();
      }
    });
    DOM.btnCancelPaste.addEventListener('click', () => {
      DOM.pasteDrawer.classList.add('hidden');
    });
    DOM.btnSubmitPaste.addEventListener('click', async () => {
      const text = DOM.pasteTextInput.value.trim();
      if (!text) {
        showToast('Please paste some text first.');
        return;
      }
      await processRawText(text, 'Pasted Notes');
      DOM.pasteDrawer.classList.add('hidden');
    });

    // Sample Notes Chips
    DOM.sampleChips.forEach(chip => {
      chip.addEventListener('click', () => {
        loadSampleDocument(chip.dataset.sample);
      });
    });

    // Change Document Button
    DOM.btnChangeDoc.addEventListener('click', () => {
      DOM.uploadDropzone.scrollIntoView({ behavior: 'smooth' });
    });

    // Settings Segmented Controls
    DOM.countSelector.querySelectorAll('.segment-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        DOM.countSelector.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.questionCountSetting = parseInt(btn.dataset.count, 10);
      });
    });

    DOM.levelSelector.querySelectorAll('.segment-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        DOM.levelSelector.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.difficultySetting = btn.dataset.level;
      });
    });

    // Questions Tab Filter & Search
    DOM.inputSearchQuestions.addEventListener('input', renderQuestionsList);
    DOM.filterTopicSelect.addEventListener('change', renderQuestionsList);
    DOM.filterLevelSelect.addEventListener('change', renderQuestionsList);

    // Start Practice From Set
    DOM.btnStartPracticeFromSet.addEventListener('click', startPracticeSession);

    // Download Menu Toggle
    DOM.btnDownloadMenu.addEventListener('click', (e) => {
      e.stopPropagation();
      DOM.downloadDropdown.classList.toggle('hidden');
    });
    document.addEventListener('click', () => {
      DOM.downloadDropdown.classList.add('hidden');
    });

    // Practice Tab Interactions
    DOM.practiceAnswerInput.addEventListener('input', updateWordCount);
    DOM.btnPracticeDictate.addEventListener('click', toggleSpeechDictation);

    DOM.btnTogglePracticeHint.addEventListener('click', () => {
      const isHidden = DOM.practiceHintDrawer.classList.contains('hidden');
      DOM.practiceHintDrawer.classList.toggle('hidden');
      DOM.tipArrow.innerHTML = isHidden ? '&#9652;' : '&#9662;';
    });

    DOM.btnCheckAnswer.addEventListener('click', checkStudentAnswer);
    DOM.btnSkipPractice.addEventListener('click', skipCurrentPracticeQuestion);
    DOM.btnFinishPracticeEarly.addEventListener('click', finishPracticeSession);

    DOM.btnNextPracticeQuestion.addEventListener('click', () => {
      state.practiceIndex += 1;
      renderCurrentPracticeQuestion();
    });

    // Progress Tab Actions
    DOM.btnProgressRevise.addEventListener('click', () => {
      if (state.sessionStats.topicsRevise.size) {
        const firstTopic = Array.from(state.sessionStats.topicsRevise)[0];
        DOM.filterTopicSelect.value = firstTopic;
      }
      switchTab('tab-questions');
    });

    DOM.btnProgressTryAgain.addEventListener('click', startPracticeSession);
    DOM.btnProgressReviewAnswers.addEventListener('click', () => switchTab('tab-questions'));

    DOM.btnPracticeSaved.addEventListener('click', () => {
      const saved = state.allQuestions.filter(q => state.savedQuestionIds.has(q.question_id));
      if (saved.length) startPracticeWithQuestions(saved);
    });
  }

  // --------------------------------------------------------------------------
  // API CALLS
  // --------------------------------------------------------------------------
  async function uploadFile(file) {
    showLoader('Reading your notes…');
    const formData = new FormData();
    formData.append('file', file);

    try {
      showLoader('Finding important topics & preparing notes…');
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Upload failed');
      }

      showLoader('Finalizing notes and viva questions…');
      const data = await res.json();

      if ((data.stats && data.stats.total_words < 20) || (data.chunks && data.chunks.length === 0)) {
        showToast("We couldn’t read enough text from this file. Try a PDF with selectable text, a Word file, or a text file.");
        return;
      }

      populateDocumentData(data);
      showToast(`Notes loaded: ${file.name}`);
      DOM.docPreviewCard.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      console.error(err);
      showToast('We couldn’t read enough text from this file. Try a text file or selectable PDF.');
    } finally {
      hideLoader();
    }
  }

  async function processRawText(text, docName) {
    showLoader('Reading your notes…');
    try {
      const res = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, document_name: docName })
      });

      if (!res.ok) throw new Error('Processing failed');
      const data = await res.json();
      populateDocumentData(data);
      showToast(`Notes ready: ${docName}`);
      DOM.docPreviewCard.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      console.error(err);
      showToast('We couldn’t process this text. Please check the content.');
    } finally {
      hideLoader();
    }
  }

  async function loadSampleDocument(filename) {
    showLoader('Reading sample notes…');
    try {
      const res = await fetch(`/api/sample/${filename}`);
      if (!res.ok) throw new Error('Sample not found');
      const sample = await res.json();
      const prettyName = filename.replace('.txt', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      await processRawText(sample.content, prettyName);
    } catch (err) {
      console.error(err);
      showToast('Could not load sample notes.');
      hideLoader();
    }
  }

  // --------------------------------------------------------------------------
  // UI HELPERS (LOADER & TOAST)
  // --------------------------------------------------------------------------
  function showLoader(stageText) {
    DOM.loaderStageText.textContent = stageText || 'Working…';
    DOM.friendlyLoader.classList.remove('hidden');
  }

  function hideLoader() {
    DOM.friendlyLoader.classList.add('hidden');
  }

  let toastTimer = null;
  function showToast(msg) {
    DOM.toastMessage.textContent = msg;
    DOM.appToast.classList.remove('hidden');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      DOM.appToast.classList.add('hidden');
    }, 2800);
  }

  function escapeHTML(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function capitalizeWords(str) {
    if (!str) return '';
    return str.replace(/\b\w/g, l => l.toUpperCase());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
