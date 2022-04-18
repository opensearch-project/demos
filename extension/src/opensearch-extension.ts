/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * The OpenSearch Contributors require contributions made to
 * this file be licensed under the Apache-2.0 license or a
 * compatible open source license.
 *
 * Modifications Copyright OpenSearch Contributors. See
 * GitHub history for details.
 */

import * as vscode from 'vscode';

const documents = {
    html : {
        loading     : '/html/loading.html',
        ready       : '/html/ready.html'
    },
    ready_files : {
        dashboards : '/ready.txt'
    }
};

const LOADING_INDEX = 0;
const READY_INDEX = 1;

export async function activate(
    ctx     :   vscode.ExtensionContext
) {

    ctx.subscriptions.push(
      vscode
        .commands
        .registerCommand(
          'opensearch.start',
          () => {
            OpenSearchDemoPanel
              .createOrShow(
                ctx.extensionUri
              )
          }
        )
    );

    const readFile = (fname) => vscode.workspace.fs.readFile(vscode.Uri.parse(vscode.workspace.workspaceFolders[0].uri + fname));
    const fileStat = (fname) => vscode.workspace.fs.stat(vscode.Uri.parse(vscode.workspace.workspaceFolders[0].uri + fname));    
    
    try {

      const htmlFileData = await Promise.all([
        await readFile(documents.html.loading),
        await readFile(documents.html.ready)
      ]);
      const htmlStrings = htmlFileData.map((raw) => new TextDecoder().decode(raw));
      OpenSearchDemoPanel.storeLoading(htmlStrings[LOADING_INDEX]);
      OpenSearchDemoPanel.storeReady(htmlStrings[READY_INDEX]);        
    } catch(e) {
      console.log('No HTML Found. Using built-in notices.')
    } finally {
      OpenSearchDemoPanel.setView(LOADING_INDEX);
      OpenSearchDemoPanel.createOrShow(ctx);
    }

    OpenSearchDemoPanel.presenceInterval = setInterval(async function() {
        try {
            await fileStat(documents.ready_files.dashboards);
            clearInterval(OpenSearchDemoPanel.presenceInterval);
            vscode.window.showInformationMessage('OpenSearch Dashboards is ready.');
            OpenSearchDemoPanel.setView(READY_INDEX);
        } catch {
            //ignore if not found - we expect an error here.
        }
    }, 500);

    if (vscode.window.registerWebviewPanelSerializer) {
      vscode
        .window
        .registerWebviewPanelSerializer(
          OpenSearchDemoPanel.viewType, {
            async deserializeWebviewPanel(
              panel : vscode.WebviewPanel,
              state : any
            ) {
              OpenSearchDemoPanel
                .revive(
                  panel, 
                  ctx
                );
            }
          }
        );
    }
}

class OpenSearchDemoPanel {
  public static current : OpenSearchDemoPanel | undefined;
  public static readonly viewType = 'opensearch';
  public static presenceInterval : number;

  private readonly _panel : vscode.WebviewPanel;
  private readonly _extUri : vscode.Uri;
  
  private static _currentHtml : string = "";
  private static _loading : string = "<!DOCTYPE html><head></head><body>Please wait while OpenSearch is loading.</body></html>";
  private static _ready : string = "<!DOCTYPE html><head></head><body>OpenSearch is Ready!</body></html>";
  private _disposables : vscode.Disposable[] = [];

  public static createOrShow(ctx) {
    const col = vscode.window.activeTextEditor ?
      vscode.window.activeTextEditor.viewColumn :
      undefined;

    if (OpenSearchDemoPanel.current) {
      OpenSearchDemoPanel.current._panel.reveal(col);
    } else {
      const panel = vscode.window.createWebviewPanel(
        OpenSearchDemoPanel.viewType,
        'OpenSearch',
        col || vscode.ViewColumn.One
      );
      
      OpenSearchDemoPanel.current = new OpenSearchDemoPanel(
        panel,
        ctx,
        ctx.extensionPath
      );

      
    }

    vscode.window.showInformationMessage('OpenSearch is loading.');
  }
  
  public static revive(
    panel : vscode.WebviewPanel,
    ctx
  ) {
    OpenSearchDemoPanel.current = new OpenSearchDemoPanel(
      panel, 
      ctx,
      ctx.extensionPath
    )
  }

  public static setView(id) { 
    switch(id) {
      case LOADING_INDEX : OpenSearchDemoPanel._currentHtml = OpenSearchDemoPanel._loading; break;
      case READY_INDEX : OpenSearchDemoPanel._currentHtml = OpenSearchDemoPanel._ready; break;
    }
    if (this.current) {
      this.current._panel.webview.html = OpenSearchDemoPanel._currentHtml;
    }
  };
  public static storeLoading(html) { OpenSearchDemoPanel._loading = html; }
  public static storeReady(html) { OpenSearchDemoPanel._ready = html; }

  private constructor(
    panel : vscode.WebviewPanel, 
    uri : vscode.Uri, 
    extensionPath : string
  ) {
    this._extUri = uri;
    this._panel = panel;

    this._update();

    this._panel.onDidDispose(
      () => {
        this.dispose();
      },
      null,
      this._disposables
    );
  }

  public dispose() {
    clearInterval(OpenSearchDemoPanel.presenceInterval);
    OpenSearchDemoPanel.current = undefined;
    this
      ._panel
        .dispose();
    
    while (this._disposables.length) {
      const x = this.
        _disposables
          .pop();
      if (x) { 
        x.dispose(); 
      }
    }
  }

  private _update() {
    this._panel.title = 'OpenSearch';
    this._panel.webview.html = OpenSearchDemoPanel._currentHtml;
  }

}