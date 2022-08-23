fetch('user_data.json').then(function(response){
  return response.json();
}).then(function(user_data) {
  console.log(user_data['coords'][0]);
}).catch(function(error){
  console.error('Could not retrieve file')
});