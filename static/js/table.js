window.onload = function() {
    let rows = document.querySelectorAll('table tbody tr');
    
    rows.forEach(function(row) {
        let probabilityCell = row.querySelector('td:nth-child(2)');
        
        if (probabilityCell) {
            let probability = parseFloat(probabilityCell.textContent.replace('%', '').trim());
            
            let roundedProbability = (probability * 100).toFixed(2);
            
            probabilityCell.textContent = `${roundedProbability}%`;
            
            if (roundedProbability <= 5) {
                probabilityCell.classList.add('p0');
            } else if (roundedProbability <= 10) {
                probabilityCell.classList.add('p1');
            } else if (roundedProbability <= 15) {
                probabilityCell.classList.add('p2');
            } else if (roundedProbability <= 20) {
                probabilityCell.classList.add('p3');
            } else if (roundedProbability <= 25) {
                probabilityCell.classList.add('p4');
            } else if (roundedProbability <= 30) {
                probabilityCell.classList.add('p5');
            } else if (roundedProbability <= 35) {
                probabilityCell.classList.add('p6');
            } else if (roundedProbability <= 40) {
                probabilityCell.classList.add('p7');
            } else if (roundedProbability <= 45) {
                probabilityCell.classList.add('p8');
            } else {
                probabilityCell.classList.add('p9');
            }
        }
    });

    let diseaseLinks = document.querySelectorAll('.disease-link');
    diseaseLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            let diseaseName = encodeURIComponent(this.getAttribute('data-disease'));
            let searchUrl = `https://www.mayoclinic.org/search/search-results?q=${diseaseName}`;
            window.location.href = searchUrl;
        });
        link.addEventListener('mousedown', function(event) {
            if (event.button === 1) {
                event.preventDefault();
                console.log("Okay");
                let diseaseName = encodeURIComponent(this.getAttribute('data-disease'));
                let searchUrl = `https://www.mayoclinic.org/search/search-results?q=${diseaseName}`;
                window.open(searchUrl, '_blank').focus();
            }
        });
    });
};