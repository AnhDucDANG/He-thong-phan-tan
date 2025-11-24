// Fix avatar URLs - add leading slash
db.users.find({avatar_url: /^api\/users\/avatars/}).forEach(function(user) {
    var oldUrl = user.avatar_url;
    var newUrl = '/' + oldUrl;
    
    db.users.updateOne(
        {_id: user._id},
        {$set: {avatar_url: newUrl}}
    );
    
    print('✅ Fixed: ' + user.email);
    print('   Old: ' + oldUrl);
    print('   New: ' + newUrl);
});

print('\n✅ Done!');
