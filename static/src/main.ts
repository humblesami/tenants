import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';
import { ChatComponent } from './components/chat/chat.component';
import { DocumentComponent } from './components/document/document.component';
import { CommentsComponent } from './components/comments/comments.component';
import { MessengerComponent } from './components/messenger/messenger.component';
import { MessageiconComponent } from './components/messageicon/messageicon.component';

import {DynamicNg2Loader} from './app/dynamicngloader';

if (environment.production) {
  enableProdMode();
}

platformBrowserDynamic().bootstrapModule(AppModule).then(function(ng2ModulerRef){
  
  let ng2Loader = new DynamicNg2Loader(ng2ModulerRef.injector);
  let components={chat:ChatComponent,messenger:MessengerComponent,messengericon:MessageiconComponent,document:DocumentComponent,comments:CommentsComponent}
  let loadedComponentReferences = [];

  window["loadComponent"] = function(component,target) {


    let compRef = ng2Loader.loadComponentAtDom(components[component], document.querySelector(target), (instance) => {
      // instance.value = count;
    });
    loadedComponentReferences.push(compRef);
  };

  window["destroyComponents"] = function () {
    loadedComponentReferences.forEach(compRef => {
      compRef.destroy();
    });
  }
}).catch(err => console.log(err));
