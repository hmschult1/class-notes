(function () {
  const layout = document.querySelector('.layout');
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');

  const modalOverlay = document.getElementById('modal-overlay');
  const modalClose = document.getElementById('modalClose');
  const modalCancel = document.getElementById('modalCancel');
  const editForm = document.getElementById('editForm');

  const inputId = document.getElementById('entryId');
  const inputName = document.getElementById('entryName');
  const inputDate = document.getElementById('entryDate');
  const inputDesc = document.getElementById('entryDescription');

  const notification = document.getElementById('notification');
  const notificationText = document.getElementById('notification-text');

  // Sidebar toggle (desktop collapsible; mobile slide-in)
  sidebarToggle?.addEventListener('click', () => {
    const mobile = window.matchMedia('(max-width: 720px)').matches;
    if (mobile) {
      layout.classList.toggle('show-sidebar');
    } else {
      layout.classList.toggle('collapsed');
    }
    const expanded = sidebarToggle.getAttribute('aria-expanded') === 'true';
    sidebarToggle.setAttribute('aria-expanded', String(!expanded));
  });

  // Modal open helpers
  function openModal() {
    modalOverlay.classList.add('open');
    modalOverlay.setAttribute('aria-hidden', 'false');
    inputName.focus();
  }

  function closeModal() {
    modalOverlay.classList.remove('open');
    modalOverlay.setAttribute('aria-hidden', 'true');
  }

  modalClose?.addEventListener('click', closeModal);
  modalCancel?.addEventListener('click', closeModal);
  modalOverlay?.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // Attach edit button handlers
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.edit-btn');
    if (!btn) return;

    const id = btn.dataset.id;
    const name = btn.dataset.name || '';
    const date = btn.dataset.date || '';
    const description = btn.dataset.description || '';

    inputId.value = id;
    inputName.value = name;
    inputDate.value = date;
    inputDesc.value = description;

    openModal();
  });
})();
