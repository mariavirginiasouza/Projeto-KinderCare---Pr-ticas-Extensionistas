document.addEventListener('DOMContentLoaded', function () {
  const container = document.querySelector('.filtro-terapeutas');

  if (!container) return;

  
  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = 'Buscar terapeuta...';
  input.style.marginBottom = '10px';
  input.style.width = '100%';

  // insere antes da lista
  container.parentNode.insertBefore(input, container);

  const labels = container.querySelectorAll('label');

  input.addEventListener('keyup', function () {
    const termo = input.value.toLowerCase();

    labels.forEach(label => {
      const texto = label.innerText.toLowerCase();
      label.style.display = texto.includes(termo) ? '' : 'none';
    });
  });
});