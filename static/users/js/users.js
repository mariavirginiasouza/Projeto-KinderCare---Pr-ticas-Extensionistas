document.addEventListener('DOMContentLoaded', function() {
    // 1. Busca o campo de senha que o Django gerou
    const campoSenha = document.getElementById('id_password');
    
    // Se o campo de senha existir na página atual...
    if (campoSenha) {
        
        // 2. Cria a estrutura HTML do "Mostrar senha"
        const container = document.createElement('div');
        container.style.marginTop = '8px';
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.gap = '6px';
        
        container.innerHTML = `
            <!-- Texto do lado esquerdo -->
            <span style="font-size: 0.85rem; color: #4b5563; cursor: pointer;" onclick="document.getElementById('toggle-senha').click()">
                Mostrar senha
            </span>
            
            <!-- Estrutura isolada do interruptor -->
            <label class="switch-container">
                <input type="checkbox" id="toggle-senha">
                <span id="toggle-slider"></span>
            </label>
        `;

        
        // 3. Insere o container logo após o campo de senha
        campoSenha.parentNode.appendChild(container);
        
        // 4. Cria a lógica de alternar entre 'password' e 'text'
        const checkbox = container.querySelector('#toggle-senha');
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                campoSenha.type = 'text';
            } else {
                campoSenha.type = 'password';
            }
        });
    }
});
