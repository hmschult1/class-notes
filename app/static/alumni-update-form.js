(function(){
  document.addEventListener('DOMContentLoaded', function(){
    function qs(sel){return document.querySelector(sel)}
    function qsa(sel){return Array.from(document.querySelectorAll(sel))}

    const volunteer_options_container = qs('#volunteer_options_container');
    const other_volunteer_container = qs('#other_volunteer_container');
    const volunteer_radios = qsa('input[name="volunteer_radio"]');
    const volunteer_choices = qsa('input[name="volunteer_choices"]');

    function updateVolunteerVisibility(){
      let anyYes=false;
      for(const r of volunteer_radios){ if(r.checked && (r.value.toLowerCase()==='yes' || r.value==='1')) anyYes=true }
      if(volunteer_options_container) volunteer_options_container.style.display = anyYes ? 'block' : 'none';

      let otherChecked=false;
      for(const c of volunteer_choices){ if(c.checked && (c.value.toLowerCase()==='other' || c.value==='Other')) otherChecked=true }
      if(other_volunteer_container) other_volunteer_container.style.display = otherChecked ? 'block' : 'none';
    }

    volunteer_radios.forEach(r=> r.addEventListener('change', updateVolunteerVisibility));
    volunteer_choices.forEach(c=> c.addEventListener('change', updateVolunteerVisibility));
    updateVolunteerVisibility();

    // Admin modal: map data-d* attributes into modal inputs when edit links clicked
    qsa('.edit-link').forEach(link=>{
      link.addEventListener('click', function(e){
        e.preventDefault();
        const modal = qs('#editModal');
        if(!modal) return;
        const mapping = {
          'dfirst':'first_name','dlast':'last_name','dmaiden':'maiden_name','demail':'email','dphone':'phone',
          'daddress1':'address_line1','daddress2':'address_line2','dcity':'city','dstate':'state','dzip':'postal_code','dcountry':'country',
          'dmarital':'marital_status','dspouse':'spouse_name','dmarrydate':'marry_date','demployer':'employer','dposition':'position',
          'deducation':'institution','dupdates':'additional_updates','dother':'other_volunteer','dnote':'class_note_text','id':'note_id','did':'note_id'
        };
        for(const dataKey in mapping){
          const inputName = mapping[dataKey];
          const val = link.dataset[dataKey] || '';
          const input = modal.querySelector('[name="'+inputName+'"]');
          if(!input) continue;
          if(input.type==='checkbox'){
            // multiple checkboxes: set checked where value in comma list
            const vals = val.split(',').map(s=>s.trim()).filter(Boolean);
            const boxes = modal.querySelectorAll('[name="'+inputName+'"]');
            if(boxes.length){
              boxes.forEach(b=> b.checked = vals.includes(b.value));
            } else {
              input.checked = vals.includes(input.value);
            }
          } else if(input.type==='radio'){
            const radios = modal.querySelectorAll('[name="'+inputName+'"]');
            radios.forEach(r=> r.checked = (r.value === val));
          } else {
            input.value = val;
          }
        }

        const volunteerRaw = link.dataset.dvolunteer || '';
        if(volunteerRaw && modal.querySelector('#volunteer_options_container')){
          modal.querySelector('#volunteer_options_container').style.display = 'block';
        }

        if(typeof bootstrap !== 'undefined'){
          const bm = bootstrap.Modal.getOrCreateInstance(modal);
          bm.show();
        } else {
          modal.style.display='block';
        }
      })
    })

  });
})();
