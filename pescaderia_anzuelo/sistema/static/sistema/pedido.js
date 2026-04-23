function autoPrint(){
    // Pequeño delay para que el navegador renderice el ticket completo
    setTimeout(() => window.print(), 300);
}

document.addEventListener('DOMContentLoaded', () => {
    const printBtn = document.getElementById('printBtn');
    if(printBtn){
        printBtn.addEventListener('click', () => window.print());
    }
    autoPrint();
});

