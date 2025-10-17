document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('modalPago');
  const openModalBtn = document.getElementById('openModal');
  const closeBtn = document.querySelector('.close');

  openModalBtn.addEventListener('click', () => {
    modal.style.display = 'block';
  });

  closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
  });

  window.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });
});
