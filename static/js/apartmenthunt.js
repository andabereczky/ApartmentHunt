// Go to the search page for the specified site.
function go_search()
{
	var selected_site_id = document.getElementById("select_site").value;
	window.location = "/apartmenthunt/" + selected_site_id + "/search/";
}

// Go to the data collection page for the specified site.
function go_collect_data()
{
	var selected_site_id = document.getElementById("select_site").value;
	window.location = "/apartmenthunt/" + selected_site_id + "/datacollection/";
}
