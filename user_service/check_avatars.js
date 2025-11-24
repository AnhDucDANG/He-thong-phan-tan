// Check current avatar URLs
db.users.find({avatar_url: {$exists: true}}, {email: 1, avatar_url: 1}).forEach(function(u) {
    print(u.email + ': ' + u.avatar_url);
});
