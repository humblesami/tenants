export class Attachment{
    id: number;
    name: string;
    url: string;
    message: Message;
    constructor()
    {
        console.log('Message constructor');        
    }
}

export class Message{
    id: number;
    from: ChatClient;
    body:string;
    create_date: string;
    uuid: string;
    sender: BaseClient;
    attachments:Array<Attachment>;
    constructor(){
        console.log('message constructor');
    }    
}

export class BaseClient{
    id: number;
    name: string;
    photo:string;    
    constructor(){
        console.log('Base client constructor');
    }
}

export class UserGroup{
    id: number;
    name: string;
}

export class AppUser extends BaseClient{    
    token: string;
    photo: '';
    user_photo: '';
    groups: Array<UserGroup>;
    constructor(){
        super();
        console.log('App User constructor');
    }
}

export class ChatClient extends BaseClient{
    id: number;
    name: string;
    photo:string;
    read:Boolean;
    unseen: number;
    is_group: Boolean;
    online: Boolean;
    messages:Array<Message>;
    constructor(){
        super();
        console.log('Chat client constructor');
    }    
}

export class ChatGroupMessage extends Message{    
    parent_message: Message;
    chat_group: ChatGroup;
}

export class UserMessage extends Message{
    sender: ChatUser;
    receiver: ChatUser;
}

export class ChatUser extends ChatClient{
    
}

export class ChatGroup extends ChatClient{        
    members: Array<ChatUser>;
    show_members: Boolean;
    created_by: ChatUser;
    constructor(){
        super()
        console.log('Chat Group constructor');      
        this.members = [];
        this.is_group = true;
    }
}