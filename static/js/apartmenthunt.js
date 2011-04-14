// Go to the search page for the specified site.
function go_search()
{
	var selected_site_subdomain = document.getElementById("select_site").value;
	if (selected_site_subdomain)
	{
		window.location = "/apartmenthunt/" + selected_site_subdomain + "/search/";
	}
}
