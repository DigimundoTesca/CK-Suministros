$(function() {
  /**
   * It records the records of "Ticket Details" and eliminates the id's of repeated tickets.
   * Color the "Ticket Details" records associated with the same ticket.
   */
  function format_tables() {
    const objects = $('tr');
    let list_id = [];
    let list_aux = [];
    let list_color = [];
    let color = [];
    let the_color=['#FFAB77','#5CB28D','#75E3B3'];
    let a = 0;
    let b = 0;
    let c = 1;
    let col = 0;
    let count = -1;

    /**
     * Format lists so that they only contain integers and ignores the head.
     */
    objects.each(function(index, element) {
      let id_element = parseInt($(element).find('th.id_kitchen_table').text().trim());
      if (!isNaN(id_element)) {
        list_id.push(id_element);
        list_aux.push(id_element);
        list_color.push(id_element);
      }
    });

    /**
     * Change the text for each item in the list.
     */
    for (let j=0; j<list_id.length; j++){
      let a = j;
      let b = j+1;

      if (list_aux[a] ===  list_id[b]){
        list_id[b] = " ";
      }
    }

    /**
     * Associates a color with each item in the list.
     */
    for (let i=0; i<=list_aux.length; i++){
      let r = i;
      let t = i+1;
      if (list_aux[r] == list_color[t]){
        c++;
      }else{
        for(q=0;q<c;q++)
        {
          color.push(the_color[col]);
        }
          col++;
          c=1;
      }
        if(col==3)
        {
          col=0;
        }
    }

    /**
     * Applies changed text to items in the list.
     * Applies the new color to items in the list.
     */
    objects.each(function(index, element) {
      let id_element = parseInt($(element).find('th.id_kitchen_table').text(list_id[count]));
      id_element = parseInt($(element).css('background',color[count]));
      count++;
    });
  }

  /**
   * Reload the page every time
   */
  function rel(){
    location.reload();
  }

  format_tables();
  setTimeout(rel, 15000);
});
